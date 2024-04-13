from pyvis.network import Network
from .tools import Vk, UserInfo
from typing import List
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
