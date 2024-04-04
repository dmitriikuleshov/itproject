import re
import vk_api
from datetime import datetime


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
                    user_id = resolved_name['object_id'] if resolved_name['type'] != 'application' else None
                    if user_id is None:
                        raise TypeError
                    if resolved_name['type'] == 'group':
                        user_id = -user_id
                except KeyError:
                    raise TypeError
            return user_id
        else:
            raise TypeError

    def get_info(self, link: str) -> dict:
        """
        Метод, возвращающий полную информацию о пользователе по ссылке.
        :param link: str
        :return: dict
        """
        return self.__vk.users.get(user_ids=self.get_id_from_link(link),
                                   fields='photo_id, verified, sex, bdate, '
                                          'city, country, home_town, has_photo, '
                                          'photo_50, photo_100, photo_200_orig, '
                                          'photo_200, photo_400_orig, photo_max, '
                                          'photo_max_orig, online, lists, domain, '
                                          'has_mobile, contacts, site, education, '
                                          'universities, schools, status, last_seen, '
                                          'followers_count, common_count, occupation, '
                                          'nickname, relatives, relation, personal, '
                                          'connections, exports, wall_comments, '
                                          'activities, interests, music, movies, tv, '
                                          'books, games, about, quotes, can_post, '
                                          'can_see_all_posts, can_see_audio, '
                                          'can_write_private_message, can_send_friend_request, '
                                          'is_favorite, is_hidden_from_feed, timezone, screen_name, '
                                          'maiden_name, crop_photo, is_friend, friend_status, '
                                          'career, military, blacklisted, blacklisted_by_me')[0]

    @staticmethod
    def valid(key: str, obj: dict):
        """
        Метод, возвращающий значение по ключу словаря
        или None в случае отсутствия введённого ключа ва словаре
        :param key: str
        :param obj: dict
        :return: Any
        """
        if key in obj.keys():
            return obj[key]
        return None

    def get_gg(self, link: str, items_count: int = 5) -> dict:
        """
        Метод для получения подробных сведений о пользователе
        VK и возвращения словаря с ними
        :param link: str
        :param items_count: int
        :return: dict
        """
        _id = self.get_id_from_link(link)
        raw = self.__vk.users.get(user_id=_id, fields='first_name, last_name, bdate, country, city, activities, '
                                                      'books, education, games, interests, movies, music, personal, '
                                                      'relatives, counters')[0]
        friends_ids = self.__vk.friends.get(user_id=_id, order='hints')
        friends, sub_users, sub_groups = [], [], []

        for elem in friends_ids['items'][:items_count]:
            d = self.__vk.users.get(user_id=elem, fields='first_name, last_name')[0]
            friends.append([d['first_name'], d['last_name'], f'https://vk.com/id{elem}'])

        subs_ids = self.__vk.users.getSubscriptions(user_id=_id)
        for elem in subs_ids['users']['items'][:items_count]:
            d = self.__vk.users.get(user_id=elem, fields='first_name, last_name')[0]
            sub_users.append([d['first_name'], d['last_name'], f'https://vk.com/id{elem}'])

        for elem in subs_ids['groups']['items'][:items_count]:
            d = self.__vk.groups.getById(group_id=elem, fields='name, screen_name')[0]
            sub_groups.append([d['name'], f'https://vk.com/{d["screen_name"]}'])

        posts = self.__vk.wall.get(owner_id=_id, count=100)

        data = {
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
            'friends_count': int(raw['counters']['friends']),
            'followers_count': int(raw['counters']['followers']),
            'friends': friends,
            'subscriptions': {
                'users': sub_users,
                'groups': sub_groups
            },
            'post_dates': [datetime.fromtimestamp(
                int(item['date'])
            ).strftime('%Y-%m-%d %H:%M:%S') for item in posts['items']]
        }

        return data
