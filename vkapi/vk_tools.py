import re
import vk_api

from vk_api.exceptions import ApiError

from datetime import datetime
from time import time

from .toxicity_check import check_obscene_vocabulary
from typing import List, TypedDict, Optional, Tuple, Dict


class University(TypedDict, total=False):
    name: Optional[str]
    faculty: Optional[str]
    form: Optional[str]
    graduation: Optional[int]


class Subscriptions(TypedDict, total=False):
    users: List[int]
    groups: List[int]


class UserInfo(TypedDict, total=False):
    id: int
    first_name: str
    last_name: str
    birthday: Optional[int]
    country: Optional[str]
    city: Optional[str]
    interests: List[str]
    books: List[str]
    games: List[str]
    movies: List[str]
    activities: List[str]
    music: List[str]
    university: Optional[University]
    relatives: List[str]
    friends_count: Optional[int]
    followers_count: Optional[int]
    friends: List[int]
    subscriptions: Optional[Subscriptions]
    post_dates: List[int]
    icon: Optional[str]


class Vk:
    """
    Класс, отвечающий за подключение к VK API

    Attributes
    ----------
    __vk: VkApiMethod
        Объект для доступа к методам VkAPI

    """

    def __init__(self, token: str) -> None:
        """
        Инициализация токена VK

        Parameters
        ----------
        token: str
            API-ключ VK

        """
        self.__vk = vk_api.VkApi(token=token).get_api()

    def get_id_from_link(self, link: str) -> str:
        """
        Метод, возвращающий ID пользователя по ссылке на его профиль

        Parameters
        ----------
        link: str
            Ссылка на анализируемый аккаунт VK

        Returns
        -------
        str
            ID пользователя

        Raises
        ------
        TypeError
            В случае некорректности ссылки на аккаунт

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
                    user_id = resolved_name['object_id'] if resolved_name['type'] == 'user' else None
                    if user_id is None:
                        raise TypeError
                except KeyError:
                    raise TypeError
            return user_id
        else:
            raise TypeError

    @staticmethod
    def convert_time(times: List[int]) -> List[str]:
        """
        Метод, принимающий список моментов времени в формате Unix
        и возвращающий список этих же моментов в формате ГГГГ-ММ-ДД ЧЧ:ММ:СС

        Parameters
        ----------
        times: List[str]
            Список моментов времени

        Returns
        -------
        List[str]
            Список преобразованных дат

        """
        return [
            datetime.fromtimestamp(
                int(item)
            ).strftime('%Y-%m-%d %H:%M:%S') for item in times
        ]

    def get_info(self, link: str) -> UserInfo:
        """
        Метод для получения подробных сведений о пользователе
        VK и возвращения словаря с ними

        Parameters
        ----------
        link: str
            Ссылка на аккаунт VK

        Returns
        -------
        UserInfo
            Словарь с данными об аккаунте VK

        """
        _id = self.get_id_from_link(link)
        raw: dict = self.__vk.users.get(user_id=_id, fields='first_name, last_name, bdate, '
                                                            'country, city, activities, '
                                                            'books, education, games, '
                                                            'interests, movies, music, personal, '
                                                            'relatives, counters, photo_50')[0]
        try:
            friends = self.__vk.friends.get(user_id=_id, order='hints')['items']
            subs = self.__vk.users.getSubscriptions(user_id=_id)
            sub_users = subs['users']['items']
            sub_groups = subs['groups']['items']
            posts = [post['date'] for post in self.__vk.wall.get(owner_id=_id, count=100)['items']]
        except ApiError:
            friends = sub_users = sub_groups = posts = None

        user_university = University(
            name=raw.get("university_name"),
            faculty=raw.get("faculty_name"),
            form=raw.get("education_form"),
            graduation=raw.get("graduation")
        )

        user_subscriptions = Subscriptions(
            users=sub_users,
            groups=sub_groups
        )

        user_info = UserInfo(
            id=int(_id),
            first_name=raw.get("first_name"),
            last_name=raw.get("last_name"),
            birthday=raw.get("bdate"),
            country=raw['country']['title'] if 'country' in raw.keys() else None,
            city=raw['city']['title'] if 'city' in raw.keys() else None,
            interests=raw.get("interests"),
            books=raw.get("books"),
            games=raw.get("games"),
            movies=raw.get("movies"),
            activities=raw.get("activities"),
            music=raw.get("music"),
            university=user_university,
            relatives=raw.get("relatives"),
            friends_count=raw["counters"].get("friends"),
            followers_count=raw["counters"].get("followers"),
            friends=friends,
            subscriptions=user_subscriptions,
            post_dates=posts,
            icon=raw.get("photo_50")
        )
        return user_info

    def get_info_short(self, link: str) -> UserInfo:
        """
        Метод, возвращающий краткую информацию об аккаунте VK.

        Parameters
        ----------
        link: str
            Ссылка на аккаунт VK

        Returns
        -------
        UserInfo
            Словарь с данными об аккаунте VK

        """
        _id = self.get_id_from_link(link)
        raw = self.__vk.users.get(user_id=_id, fields='first_name, last_name, photo_50')[0]
        user_info = UserInfo(
            id=int(_id),
            first_name=raw.get("first_name"),
            last_name=raw.get("last_name"),
            icon=raw.get("photo_50")
        )
        return user_info

    def get_users_list_info(self, users_ids_list: List[int]) -> List[UserInfo]:
        """
        Метод, возвращающий список данных о нескольких аккаунтах VK

        Parameters
        ----------
        users_ids_list: List[int]
            Ссылка на аккаунт VK

        Returns
        -------
        List[UserInfo]
            Список с объектами данных о пользователях

        """
        raw = self.__vk.users.get(user_ids=users_ids_list, fields='first_name, last_name, photo_50')
        users_info_list = []
        for raw_user in raw:
            user_info = UserInfo(
                id=int(raw_user["id"]),
                first_name=raw_user.get("first_name"),
                last_name=raw_user.get("last_name"),
                icon=raw_user.get("photo_50")
            )
            users_info_list.append(user_info)
        return users_info_list

    def get_links_by_ids(self, user_data: UserInfo, count: Tuple[int] = (5, 5, 5)) -> Dict[str, List[List[str]]]:
        """
        Метод, принимающий словарь с данными о пользователе и кортеж с количествами
        ссылок, которые необходимо получить для каждой категории,
        и возвращающий словарь с именами и ссылками на друзей, аккаунты и группы,
        на которые подписан пользователь('friends', 'users', 'groups' соответственно)

        Parameters
        ----------
        user_data: UserInfo
            Данные об аккаунте VK
        count: Tuple[int]
            Ограничители количества ссылок

        Returns
        -------
        Dict[str, List[List[str]]]
            Словарь со списками ссылок на друзей и подписки

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

    def get_activity(self, user_data: UserInfo, count: Tuple[int] = (5, 5, 5), time_limit: int = 2629743,
                     times: bool = True) -> List[str] | List[Tuple[str]]:
        """
        Метод, принимающих словарь с данными о пользователе и
        возвращающий список с датами и временами публикаций постов
        пользователем и оставлений им комментариев под постами
        друзей, пользователей или групп, на которые он подписан,
        если times = True, и список текстов этих постов в противном случае.
        Рассматриваются посты, выложенные не ранее, чем за
        time_limit секунд дл текущего момента

        Parameters
        ----------
        user_data: UserInfo
            Данные об аккаунте VK
        count: Tuple[int]
            Ограничители количества ссылок
        time_limit: int
            Ограничитель возраста рассматриваемых постов
        times: bool
            Режим работы (моменты времени или тексты для анализа токсичности)

        Returns
        -------
        List[str] | List[Tuple[str]]
            Список с моментами времени или с кортежами текстов и ссылок на посты

        """
        result = set()

        if user_data['friends'] is not None:
            for friend in user_data['friends'][:count[0]] + [user_data['id']]:
                try:
                    posts = self.__vk.wall.get(owner_id=friend, count=100)
                    for post in posts['items']:
                        if post['date'] < time() - time_limit:
                            break
                        if post['comments']['count']:
                            comments = self.__vk.wall.getComments(owner_id=friend, post_id=post['id'], count=100)
                            for comment in comments['items']:
                                if comment['from_id'] == user_data['id']:
                                    if times:
                                        result.add(comment['date'])
                                    else:
                                        result.add((comment['text'],
                                                    f'https://vk.com/wall{user_data["id"]}_{post["id"]}'))
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
                                    if times:
                                        result.add(comment['date'])
                                    else:
                                        result.add((comment['text'],
                                                    f'https://vk.com/wall{user_data["id"]}_{post["id"]}'))
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
                                    if times:
                                        result.add(comment['date'])
                                    else:
                                        result.add((comment['text'],
                                                    f'https://vk.com/wall{user_data["id"]}_{post["id"]}'))
                except ApiError:
                    pass

        if times:
            if user_data['post_dates'] is not None:
                return self.convert_time(sorted(list(result) + user_data['post_dates']))
            return list(result)

        posts = self.__vk.wall.get(owner_id=user_data['id'], count=100)
        return list(result) + [(post['text'],
                                f'https://vk.com/wall{user_data["id"]}_{post["id"]}') for post in posts['items']]

    def check_toxicity(self, user_data: UserInfo) -> List[Optional[str]]:
        """
        Метод, проверяющий массив постов и комментариев пользователя
        на предмет наличия нецензурной и оскорбительной лексики
        и возвращающий список сообщений, в которых такая лексика была найдена

        Parameters
        ----------
        user_data: UserInfo
            Данные об аккаунте VK

        Returns
        -------
        List[Optional[str]]
            Список со ссылками на тексты с нецензурной лексикой

        """
        return check_obscene_vocabulary(self.get_activity(user_data, times=False))

    def get_mutual_friends(self, *links: Tuple[str]) -> List[UserInfo] | None:
        """
        Метод, принимающий кортеж ссылок на пользователей и возвращающий
        List[UserInfo] - список информации об общих друзьях (UserInfo) для переданных ссылок.
        В случае ошибки при получении информации о друзьях для одного из пользователей,
        возвращает None (если профиль скрыт).

        :param links: Tuple[str]
        :return: List[UserInfo] | None
        """
        _ids = [self.get_id_from_link(link) for link in links]
        _friends_sets = []
        for _id in _ids:
            try:
                friends = set(self.__vk.friends.get(user_id=_id, count=10)["items"])
                _friends_sets.append(friends)
            except Exception as e:
                # print(f"Ошибка при получении списка друзей для пользователя с ID {_id}: {e}")

                return None
        mutual_friends = set.intersection(*_friends_sets)
        return self.get_users_list_info(list(mutual_friends))

    def get_common_connections(
            self, link: str
    ) -> List[Tuple[UserInfo, Optional[List[UserInfo]]]]:
        """
        метод, принимающий ссылку на пользователя
        и возвращий список кортежей, где каждый кортеж содержит
        информацию о друге пользователя и список их общих друзей с переданным пользователем.

        :param link: str
        return: List[Tuple[UserInfo, Optional[List[UserInfo]]]] | None
        """
        _id = self.get_id_from_link(link)
        _friends = self.__vk.friends.get(user_id=_id, count=10)["items"]
        connections = []
        for friend in self.get_users_list_info(_friends):
            connections.append(
                (friend, self.get_mutual_friends(link, str(friend.get("id"))))
            )
        return connections
