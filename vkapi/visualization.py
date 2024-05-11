from pyvis.network import Network
from .vk_tools import Vk, UserInfo
from typing import List, Tuple, Optional, Union
from copy import deepcopy
import pandas as pd
from collections import Counter
from datetime import datetime, timedelta
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
        music = self.user_info.get("music")
        if music is not None and len(music) > 3:
            return self.user_info.get("music")[:3]
        return music

    def create_activity_graph(self, link_to_save_graph: str) -> None:
        # Загрузка данных активности пользователя
        post_dates = self.vk.get_activity(self.user_info, times=True)

        # Если список дат пуст, устанавливаем диапазон дат за последний год
        if not post_dates:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=365)
            date_range = pd.date_range(start=start_date, end=end_date).date
        else:
            # Преобразование дат в формат даты
            post_dates = pd.to_datetime(post_dates).date

            # Создание полного списка дат на основе минимальной и максимальной даты
            start_date = min(post_dates)
            end_date = max(post_dates)
            date_range = pd.date_range(start=start_date, end=end_date).date

        # Создание DataFrame с нулевыми значениями для каждой даты
        df = pd.DataFrame(date_range, columns=['Date'])
        df['Number of Posts'] = 0

        # Создание временного ряда
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(x=df['Date'], y=df['Number of Posts'])
        )

        # Задание заголовка графика и размера графика
        fig.update_layout(
            title_text="User Posts Over Time with Range Slider",
            height=600,  # Установка высоты графика в пикселях
            width=900  # Установка ширины графика в пикселях
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