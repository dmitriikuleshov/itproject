from pyvis.network import Network
from .vk_tools import Vk, UserInfo, GroupInfo
from typing import List, Union, Tuple
from copy import deepcopy
import pandas as pd
from collections import Counter
from datetime import datetime
import plotly.graph_objects as go
import os


class Visualization:
    def __init__(self, link: str):
        self.vk = Vk(token=os.environ['VK_TOKEN'])
        self.link = link
        self.user_info: UserInfo = self.vk.get_info(link)
        self.vk_mutual_friends_info = None
        self.mutual_graph = Network(height='750px', width='700px', bgcolor='#222222', font_color='white')
        self.activity_graph = None

    def create_mutual_friends_graph(self, link_to_save_graph: str) -> None:
        self.vk_mutual_friends_info = self.vk.get_common_connections(self.link)

        self.mutual_graph.add_node(n_id=-1,
                                   label=f'{self.user_info["first_name"]} {self.user_info["last_name"]}',
                                   shape="circularImage",
                                   image=self.user_info["icon"], font={'size': 10}, size=25)

        cur_id = 0
        id_dict: dict = dict()
        for friend_info in self.vk_mutual_friends_info:
            self.mutual_graph.add_node(n_id=cur_id,
                                       label=f'{friend_info[0].get("first_name")} {friend_info[0].get("last_name")}',
                                       shape="circularImage",
                                       image=friend_info[0].get("icon"),
                                       font={"size": 10},
                                       size=15)
            friend_id = deepcopy(cur_id)
            id_dict[friend_info[0].get("id")] = friend_id
            self.mutual_graph.add_edge(-1, cur_id)
            cur_id += 1

        for friend_info in self.vk_mutual_friends_info:
            if friend_info[1] is not None:
                for friend_friend in friend_info[1]:
                    self.mutual_graph.add_edge(
                        id_dict[friend_friend.get("id")],
                        id_dict[friend_info[0].get("id")]
                    )

        # saving graph
        self.mutual_graph.save_graph(link_to_save_graph)

    def get_favourite_music(self) -> Union[List[str], None]:
        music = self.user_info["music"]
        print(music)

        if music is not None and len(music) > 3:
            return music[:3]
        return music

    def get_toxicity(self) -> Tuple[str, List[str]]:
        try:
            toxic_posts = self.vk.check_toxicity(self.user_info)
            toxicity_coeff = self.get_toxicity_coefficient()
            return toxicity_coeff, toxic_posts
        except TypeError:
            return "У пользователя нет постов или он ограничил доступ к своим записям", []

    def get_toxicity_coefficient(self) -> str:
        all_posts = self.vk.get_activity(self.user_info, times=True)
        if all_posts is None or len(all_posts) == 0:
            return "У пользователя нет постов или он ограничил доступ к своим записям"
        return str(round((len(self.vk.check_toxicity(self.user_info)) /
                          len(all_posts)), 2))

    def get_user_subscriptions(self) -> List[UserInfo]:
        subscriptions = self.user_info.get("subscriptions")
        user_subscriptions = subscriptions.get("users")
        if user_subscriptions is not None:
            if len(user_subscriptions) > 5:
                user_subscriptions = user_subscriptions[:5]
            return self.vk.get_users_list_info(user_subscriptions)
        return []

    def get_group_subscriptions(self) -> List[GroupInfo]:
        subscriptions = self.user_info.get("subscriptions")
        group_subscriptions = subscriptions.get("groups")
        if group_subscriptions is not None:
            if len(group_subscriptions) > 5:
                group_subscriptions = group_subscriptions[:5]
            return self.vk.get_groups_list_info(group_subscriptions)
        return []

    def create_activity_graph(self, link_to_save_graph: str) -> None:
        # Загрузка данных активности пользователя
        post_dates_raw = self.vk.get_activity(self.user_info, times=True)

        # Преобразование дат в формат даты
        post_dates = pd.to_datetime(post_dates_raw).date

        # Подсчет количества постов в каждую дату
        date_counts = Counter(post_dates)

        # Создание полного списка дат в диапазоне дат активности пользователя
        if len(post_dates) > 0:
            start_date = min(post_dates)
        else:
            start_date = pd.to_datetime(['2015-01-01 00:00:01']).date[0]
        end_date = datetime.now()
        all_dates = pd.date_range(start=start_date, end=end_date).date

        # Создание DataFrame с нулевыми значениями для каждой даты
        all_dates_df = pd.DataFrame(all_dates, columns=['Date'])
        all_dates_df['Number of Posts'] = 0

        # Преобразование данных активности пользователя в DataFrame
        activity_df = pd.DataFrame(list(date_counts.items()), columns=['Date', 'Number of Posts'])

        # Объединение данных активности пользователя с полным списком дат
        final_df = pd.merge(all_dates_df, activity_df, on='Date', how='left')
        final_df['Number of Posts'] = final_df['Number of Posts_y'].fillna(0).astype(int)

        # Создание временного ряда
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(x=final_df['Date'], y=final_df['Number of Posts'])
        )

        # Задание заголовка графика
        fig.update_layout(
            title_text="User Posts Over Time with Range Slider"
        )

        # Добавление ползунка выбора диапазона
        fig.update_layout(
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all")
                    ])
                ),
                rangeslider=dict(
                    visible=True
                ),
                type="date"
            )
        )

        # Сохранение графика в HTML-файл по указанному пути
        fig.write_html(link_to_save_graph)
