from .vk_tools import Vk, UserInfo
from typing import List
import os


class Visualization:
    def __init__(self, link: str):
        self.vk = Vk(token=os.environ['VK_TOKEN'])
        self.link = link
        self.user_info: UserInfo = self.vk.get_info(link)
