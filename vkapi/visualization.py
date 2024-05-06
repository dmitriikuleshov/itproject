from pyvis.network import Network
from .vk_tools import Vk, UserInfo
from typing import List, Tuple, Optional
from copy import deepcopy
import os


class Visualization:
    def __init__(self, link: str):
        self.vk = Vk(token=os.environ['VK_TOKEN'])
        self.link = link
        self.user_info: UserInfo = self.vk.get_info(link)
        self.vk_mutual_friends_info = None

    def create_mutual_friends_graph(self, link_to_save_graph: str) -> None:
        self.vk_mutual_friends_info = self.vk.get_common_connections(self.link)
        # create graph object
        graph = Network(height='750px', width='700px', bgcolor='#222222', font_color='white')

        graph.add_node(n_id=-1, label=f'{self.user_info["first_name"]} {self.user_info["last_name"]}',
                       shape="circularImage",
                       image=self.user_info["icon"], font={'size': 10}, size=25)

        cur_id = 0
        id_dict: dict = dict()
        for friend_info in self.vk_mutual_friends_info:
            graph.add_node(n_id=cur_id,
                           label=f'{friend_info[0].get("first_name")} {friend_info[0].get("last_name")}',
                           shape="circularImage",
                           image=friend_info[0].get("icon"),
                           font={"size": 10},
                           size=15)
            friend_id = deepcopy(cur_id)
            id_dict[friend_info[0].get("id")] = friend_id
            graph.add_edge(-1, cur_id)
            cur_id += 1

        for friend_info in self.vk_mutual_friends_info:
            if friend_info[1] is not None:
                for friend_friend in friend_info[1]:
                    graph.add_edge(
                        id_dict[friend_friend.get("id")],
                        id_dict[friend_info[0].get("id")]
                    )

        # saving graph
        graph.save_graph(link_to_save_graph)
