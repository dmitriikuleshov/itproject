import re
import vk_api

from vk_api.exceptions import ApiError

from datetime import datetime
from time import time


class Vk:
    """Класс, отвечающий за подключение VK API."""

    def __init__(self, token: str) -> None:
        """
        Инициализация токена VK.

        :param token: str
        """
        self.__vk = vk_api.VkApi(token=token).get_api()

    def get_id_from_link(self, link: str) -> str:
        """
        Метод, возвращающий ID пользователя по ссылке на его профиль.

        :param link: str
        :return: str
        """
        id_reg_expression = (r"(^-?[\d]+)|(?:feed\?\w?=)?(?:wall|im\?sel="
                             r"|id=*|photo|videos|albums|audios|topic)(-?"
                             r"[\d]+)|(?:club|public)([\d]*)|(?<=\.com/)("
                             r"[a-zA-Z\d._]*)")
        find_results = re.findall(id_reg_expression, link)
        id_or_name = None
        if find_results:
            try:
                id_or_name = [el for el in find_results[0] if el]
                user_id = int(id_or_name[0])
            except ValueError:
                try:
                    resolved_name = self.__vk.utils.resolveScreenName(
                        screen_name=id_or_name[0])
                    print(resolved_name)
                    user_id = resolved_name['object_id'] if resolved_name['type'] == 'user' else None
                    if user_id is None:
                        raise TypeError
                except KeyError:
                    raise TypeError
            print(type(user_id))
            return user_id
        else:
            raise TypeError

    @staticmethod
    def valid(key: str, obj: dict):
        """
        Метод, возвращающий значение по ключу словаря
        или None в случае отсутствия введённого ключа в словаре

        :param key: str
        :param obj: dict
        :return: Any
        """
        if key in obj.keys():
            return obj[key]
        return None

    @staticmethod
    def convert_time(times: list) -> list:
        """
        Метод, принимающий список моментов времени в формате Unix
        и возвращающий список этих же моментов в формате ГГГГ-ММ-ДД ЧЧ:ММ:СС
        :param times: list
        :return: list
        """
        return [
            datetime.fromtimestamp(
                int(item['date'])
            ).strftime('%Y-%m-%d %H:%M:%S') for item in times
        ]

    def get_info(self, link: str) -> dict:
        """
        Метод для получения подробных сведений о пользователе
        VK и возвращения словаря с ними

        :param link: str
        :return: dict
        """
        _id = self.get_id_from_link(link)
        raw = self.__vk.users.get(user_id=_id, fields='first_name, last_name, bdate, '
                                                      'country, city, activities, '
                                                      'books, education, games, '
                                                      'interests, movies, music, personal, '
                                                      'relatives, counters, photo_50')[0]
        try:
            friends = self.__vk.friends.get(user_id=_id, order='hints')['items']
            subs = self.__vk.users.getSubscriptions(user_id=_id)
            sub_users = subs['users']['items']
            sub_groups = subs['groups']['items']
            posts = self.__vk.wall.get(owner_id=_id, count=100)
        except ApiError:
            friends = sub_users = sub_groups = posts = None

        data = {
            'id': _id,
            'first_name': self.valid('first_name', raw),
            'last_name': self.valid('last_name', raw),
            'birthday': self.valid('bdate', raw),
            'country': raw['country']['title'] if 'country' in raw.keys() else None,
            'city': raw['city']['title'] if 'city' in raw.keys() else None,
            'interests': self.valid('interests', raw),
            'books': self.valid('books', raw),
            'games': self.valid('games', raw),
            'movies': self.valid('movies', raw),
            'activities': self.valid('activities', raw),
            'music': self.valid('music', raw),
            'university': {
                'name': self.valid('university_name', raw),
                'faculty': self.valid('faculty_name', raw),
                'form': self.valid('education_form', raw),
                'graduation': self.valid('graduation', raw)
            },
            'relatives': self.valid('relatives', raw),
            'friends_count': self.valid('friends', raw['counters']),
            'followers_count': self.valid('followers', raw['counters']),
            'friends': friends,
            'subscriptions': {
                'users': sub_users,
                'groups': sub_groups
            },
            'post_dates': posts['items'],
            'icon': self.valid('photo_50', raw)
        }

        return data

    def get_links_by_ids(self, user_data: dict, count: tuple = (5, 5, 5)) -> dict:
        """
        Метод, принимающий словарь с данными о пользователе и кортеж с количествами
        ссылок, которые необходимо получить для каждой категории,
        и возвращающий словарь с именами и ссылками на друзей, аккаунты и группы,
        на которые подписан пользователь('friends', 'users', 'groups' соответственно)

        :param user_data: dict
        :param count: tuple
        :return: dict
        """
        friends, users, groups = [], [], []

        if user_data['friends'] is not None:
            for elem in user_data['friends'][:count[0]]:
                d = self.__vk.users.get(user_id=elem, fields='first_name, last_name')[0]
                friends.append([d['first_name'], d['last_name'], f'https://vk.com/id{elem}'])

        if user_data['subscriptions']['users'] is not None:
            for elem in user_data['subscriptions']['users'][:count[1]]:
                d = self.__vk.users.get(user_id=elem, fields='first_name, last_name')[0]
                users.append([d['first_name'], d['last_name'], f'https://vk.com/id{elem}'])

        if user_data['subscriptions']['groups'] is not None:
            for elem in user_data['subscriptions']['groups'][:count[2]]:
                d = self.__vk.groups.getById(group_id=elem, fields='name, screen_name')[0]
                groups.append([d['name'], f'https://vk.com/{d["screen_name"]}'])

        return {
            'friends': friends,
            'users': users,
            'groups': groups
        }

    def get_activity(self, user_data: dict, count: tuple = (40, 40, 40), time_limit: int = 2629743) -> list:
        """
        Метод, принимающих словарь с данными о пользователе и
        возвращающий список с датами и временами публикаций постов
        пользователем и оставлений им комментариев под постами
        друзей, пользователей или групп, на которые он подписан.
        Рассматриваются посты, выложенные не ранее, чем за
        time_limit секунд дл текущего момента

        :param user_data: dict
        :param count: tuple
        :param time_limit: int
        :return: list
        """
        times = set()

        if user_data['friends'] is not None:
            for friend in user_data['friends'][:count[0]]:
                try:
                    posts = self.__vk.wall.get(owner_id=friend, count=100)
                    for post in posts['items']:
                        if post['date'] < time() - time_limit:
                            break
                        if post['comments']['count']:
                            comments = self.__vk.wall.getComments(owner_id=friend, post_id=post['id'], count=100)
                            for comment in comments['items']:
                                if comment['from_id'] == user_data['id']:
                                    times.add(comment['date'])
                except ApiError:
                    pass

        if user_data['subscriptions']['users'] is not None:
            for user in user_data['friends'][:count[1]]:
                try:
                    posts = self.__vk.wall.get(owner_id=user, count=100)
                    for post in posts['items']:
                        if post['date'] < time() - time_limit:
                            break
                        if post['comments']['count']:
                            comments = self.__vk.wall.getComments(owner_id=user, post_id=post['id'], count=100)
                            for comment in comments['items']:
                                if comment['from_id'] == user_data['id']:
                                    times.add(comment['date'])
                except ApiError:
                    pass

        if user_data['subscriptions']['groups'] is not None:
            for group in user_data['friends'][:count[2]]:
                try:
                    posts = self.__vk.wall.get(owner_id=-group, count=100)
                    for post in posts['items']:
                        if post['date'] < time() - time_limit:
                            break
                        if post['comments']['count']:
                            comments = self.__vk.wall.getComments(owner_id=-group, post_id=post['id'], count=100)
                            for comment in comments['items']:
                                if comment['from_id'] == user_data['id']:
                                    times.add(comment['date'])
                except ApiError:
                    pass

        return sorted(list(times) + user_data['post_dates'])