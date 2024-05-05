from pyvis.network import Network
from .tools import Vk, UserInfo
from typing import List, Tuple, Optional
from copy import deepcopy
import os


def create_friends_graph(link_to_save_graph: str, user_info: UserInfo) -> None:
    # create graph object
    graph = Network(height='750px', width='700px', bgcolor='#222222', font_color='white')

    # add main account
    graph.add_node(n_id=-1, label=f'{user_info["first_name"]} {user_info["last_name"]}', shape="circularImage",
                   image=user_info["icon"], font={'size': 10}, size=25)

    # initializing vk parser
    vk = Vk(token=os.environ['VK_TOKEN'])

    # get list of user's friends
    if len(user_info["friends"]) > 10:
        friends_info: List[UserInfo] = vk.get_users_list_info(user_info["friends"][:10])
    else:
        friends_info: List[UserInfo] = vk.get_users_list_info(user_info["friends"])

    # adding friends
    for ind, friend in enumerate(friends_info):
        graph.add_node(n_id=ind,
                       label=f'{friend.get("first_name")} {friend.get("last_name")}',
                       shape="circularImage",
                       image=friend.get("icon"),
                       font={"size": 10},
                       size=15)
        graph.add_edge(-1, ind)

    # saving graph
    graph.save_graph(link_to_save_graph)


def create_mutual_friends_graph(link_to_save_graph: str,
                                user_info: UserInfo,
                                vk_mutual_friends_info: List[Tuple[UserInfo, Optional[List[UserInfo]]]]) -> None:
    # create graph object
    graph = Network(height='750px', width='700px', bgcolor='#222222', font_color='white')

    graph.add_node(n_id=-1, label=f'{user_info["first_name"]} {user_info["last_name"]}', shape="circularImage",
                   image=user_info["icon"], font={'size': 10}, size=25)

    cur_id = 0
    for friend_info in vk_mutual_friends_info:
        graph.add_node(n_id=cur_id,
                       label=f'{friend_info[0].get("first_name")} {friend_info[0].get("last_name")}',
                       shape="circularImage",
                       image=friend_info[0].get("icon"),
                       font={"size": 10},
                       size=15)
        friend_id = deepcopy(cur_id)
        graph.add_edge(-1, cur_id)
        cur_id += 1

        if friend_info[1] is not None:
            for friend_friend_info in friend_info[1]:
                graph.add_node(n_id=cur_id,
                               label=f'{friend_friend_info.get("first_name")} {friend_friend_info.get("last_name")}',
                               shape="circularImage",
                               image=friend_friend_info.get("icon"),
                               font={"size": 10},
                               size=15)
                graph.add_edge(friend_id, cur_id)
                graph.add_edge(-1, cur_id)

                cur_id += 1

    # saving graph
    graph.save_graph(link_to_save_graph)

