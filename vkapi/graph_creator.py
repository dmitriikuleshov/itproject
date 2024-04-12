from pyvis.network import Network
from .tools import Vk
import os


def create_friends_graph(link_to_save_graph: str, user_info: dict) -> None:
    # create graph object
    graph = Network(height='750px', width='700px', bgcolor='#222222', font_color='white')

    # add main account
    graph.add_node(n_id=-1, label=f'{user_info["first_name"]} {user_info["last_name"]}', shape="circularImage",
                   image=user_info["icon"], font={'size': 10}, size=25)

    # initializing vk parser
    vk = Vk(token=os.environ['VK_TOKEN'])

    # adding friends
    for ind, friend in enumerate(user_info["friends"][:10]):
        friend_info = vk.get_info_short(f"https://vk.com/id{friend}")
        graph.add_node(n_id=ind, label=f'{friend_info["first_name"]} {friend_info["last_name"]}', shape="circularImage",
                       image=friend_info["icon"], font={'size': 10}, size=15)
        graph.add_edge(-1, ind)

    # saving graph
    graph.save_graph(link_to_save_graph)
