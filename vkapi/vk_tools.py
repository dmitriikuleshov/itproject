"""
Описание объектов данных об аккаунтах VK, а также
класс, отвечающий за доступ к VK API
"""

import re
import vk_api

from vk_api.exceptions import ApiError
from .toxicity_check import check_obscene_vocabulary

from datetime import datetime
from time import time

from typing import List, TypedDict, Optional, Tuple


class University(TypedDict, total=False):
    """
    Словарь с данными об высшем учебном заведении,
    в котором обучался владелец аккаунта

    Attributes
    ----------
    name: Optional[str]
        Название университета
    faculty: Optional[str]
        Название факультета
    form: Optional[str]
        Форма образование (очная/заочная)
    graduation: Optional[int]
        Учёная степень

    """
    name: Optional[str]
    faculty: Optional[str]
    form: Optional[str]
    graduation: Optional[int]


class Subscriptions(TypedDict, total=False):
    """
    Словарь со списками подписок аккаунта VK
    на пользователей и сообщества

    Attributes
    ----------
    users: List[int]
        Список ID пользователей
    groups: List[int]
        Список ID сообществ

    """
    users: List[int]
    groups: List[int]


class UserInfo(TypedDict, total=False):
    """
    Словарь с основными данными об аккаунте VK

    Attributes
    ----------
    id: int
        Идентификатор пользователя
    first_name: str
        Имя пользователя
    last_name: str
        Фамилия пользователя
    birthday: Optional[int]
        Дата рождения
    country: Optional[str]
        Страна проживания
    city: Optional[str]
        Город проживания
    interests: Optional[str]
        Интересы (из профиля)
    books: Optional[str]
        Любимые книги
    games: Optional[str]
        Любимые игры
    movies: Optional[str]
        Любимые фильмы
    activities: Optional[str]
        Увлечения
    music: Optional[str]
        Любимая музыка
    university: Optional[University]
        Объект данных о высшем образовании
    relatives: List[str]
        Список имён родственников
    friends_count: Optional[int]
        Количество друзей
    followers_count: Optional[int]
        Количество подписчиков
    friends: List[int]
        Список идентификаторов друзей
    subscriptions: Optional[Subscriptions]
        Список объектов со списками подписок
    post_dates: List[int]
        Список дат публикаций постов
    icon: Optional[str]
        Ссылка на иконку пользователя

    """
    id: int
    first_name: str
    last_name: str
    birthday: Optional[int]
    country: Optional[str]
    city: Optional[str]
    interests: Optional[str]
    books: Optional[str]
    games: Optional[str]
    movies: Optional[str]
    activities: Optional[str]
    music: Optional[str]
    university: Optional[University]
    relatives: List[str]
    friends_count: Optional[int]
    followers_count: Optional[int]
    friends: List[int]
    subscriptions: Optional[Subscriptions]
    post_dates: List[int]
    icon: Optional[str]


class GroupInfo(TypedDict, total=False):
    """
    Словарь с данными о сообществе VK

    Attributes
    ----------
    id: int
        Идентификатор сообщества
    name: str
        Название сообщества
    link: str
        Ссылка на сообщество
    photo: str
        Ссылка на иконку сообщества

    """
    id: int
    name: str
    link: str
    photo: str


class Vk:
    """
    Класс, отвечающий за подключение к VK API

    Attributes
    ----------
    __vk: VkApiMethod
        Объект для доступа к методам VkAPI

    Methods
    -------
    get_id_from_link(link)
        Получение ID пользователя по ссылке
    convert_time(times)
        Преобразование формата моментов времени
    get_info(link)
        Получение информации об аккаунте
    get_info_short(link)
        Получение краткой информации об аккаунте
    get_users_list_info(users_ids_list)
        Получение краткой информации о нескольких аккаунтах
    get_groups_list_info(groups_ids_list)
        Получение краткой информации о нескольких сообществах
    get_activity(user_data, count, time_limit, times)
        Получение данных об активности аккаунта
    check_toxicity(user_data)
        Анализ публикация аккаунта на ненормативную лексику

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
        id_reg_expression = (r'(^-?[\d]+)|(?:feed\?\w?=)?(?:wall|im\?sel='
                             r'|id=*|photo|videos|albums|audios|topic)(-?'
                             r'[\d]+)|(?:club|public)([\d]*)|(?<=\.com/)('
                             r'[a-zA-Z\d._]*)')
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
        relatives = []
        if 'relatives' in raw.keys():
            relatives = [rel['name'] for rel in raw['relatives']]

        try:
            friends = self.__vk.friends.get(user_id=_id, order='hints')['items']
            subs = self.__vk.users.getSubscriptions(user_id=_id)
            sub_users = subs['users']['items']
            sub_groups = subs['groups']['items']
            posts = [post['date'] for post in self.__vk.wall.get(owner_id=_id, count=100)['items']]
        except ApiError:
            friends = sub_users = sub_groups = posts = None

        user_university = University(
            name=raw.get('university_name'),
            faculty=raw.get('faculty_name'),
            form=raw.get('education_form'),
            graduation=raw.get('graduation')
        )

        user_subscriptions = Subscriptions(
            users=sub_users,
            groups=sub_groups
        )

        user_info = UserInfo(
            id=int(_id),
            first_name=raw.get('first_name'),
            last_name=raw.get('last_name'),
            birthday=raw.get('bdate'),
            country=raw['country']['title'] if 'country' in raw.keys() else None,
            city=raw['city']['title'] if 'city' in raw.keys() else None,
            interests=raw.get('interests'),
            books=raw.get('books'),
            games=raw.get('games'),
            movies=raw.get('movies'),
            activities=raw.get('activities'),
            music=raw.get('music'),
            university=user_university,
            relatives=relatives,
            friends_count=raw['counters'].get('friends'),
            followers_count=raw['counters'].get('followers'),
            friends=friends,
            subscriptions=user_subscriptions,
            post_dates=posts,
            icon=raw.get('photo_50')
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
            first_name=raw.get('first_name'),
            last_name=raw.get('last_name'),
            icon=raw.get('photo_50')
        )
        return user_info

    def get_users_list_info(self, users_ids_list: List[int]) -> List[UserInfo]:
        """
        Метод, возвращающий список данных о нескольких аккаунтах VK

        Parameters
        ----------
        users_ids_list: List[int]
            Список ID аккаунтов VK

        Returns
        -------
        List[UserInfo]
            Список с объектами данных о пользователях

        """
        raw = self.__vk.users.get(user_ids=users_ids_list, fields='first_name, last_name, photo_50')
        list_of_user_info = []

        for raw_user in raw:
            list_of_user_info.append(UserInfo(
                id=int(raw_user['id']),
                first_name=raw_user.get('first_name'),
                last_name=raw_user.get('last_name'),
                icon=raw_user.get('photo_50')
            ))

        return list_of_user_info

    def get_groups_list_info(self, groups_ids_list: List[int]) -> List[GroupInfo]:
        """
        Метод, возвращающий список данных о нескольких сообществах VK

        Parameters
        ----------
        groups_ids_list: List[int]
            Список ID сообществ VK

        Returns
        -------
        List[GroupInfo]
            Список с объектами данных о сообществах

        """
        raw = self.__vk.groups.getById(group_ids=groups_ids_list)
        list_of_group_info = []

        for group in raw:
            list_of_group_info.append(GroupInfo(
                id=group.get('id'),
                name=group.get('name'),
                link=f'https://vk.com/{group['screen_name']}' if 'screen_name' in group.keys() else None,
                photo=group.get('photo_50')
            ))

        return list_of_group_info

    def get_activity(self, user_data: UserInfo, count: Tuple[int] = (5, 5, 5), time_limit: int = 2629743,
                     times: bool = True) -> List[str] | List[Tuple[str, str]]:
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
        def check_activity(_id: int, is_groups: bool = False) -> None:
            """
            Функция итеративной проверки активности пользователя в
            комментариях аккаунто с данным id

            Parameters
            ----------
            _id: int
                ID проверяемого аккаунта
            is_groups: bool
                Флаг, отвечающий за добавления минуса к ID группы

            """
            try:
                posts = self.__vk.wall.get(owner_id=-_id if is_groups else _id, count=100)
                for post in posts['items']:
                    if post['date'] < time() - time_limit:
                        break
                    if post['comments']['count']:
                        comments = self.__vk.wall.getComments(owner_id=-_id if is_groups else _id, post_id=post['id'],
                                                              count=100)
                        for comment in comments['items']:
                            if comment['from_id'] == user_data['id']:
                                if times:
                                    result.add(comment['date'])
                                else:
                                    result.add((str(comment['text']),
                                                f'https://vk.com/wall{user_data["id"]}_{post["id"]}'))
            except ApiError:
                pass

        result = set()

        check_activity(user_data['id'])

        if user_data['friends'] is not None:
            for friend in user_data['friends'][:count[0]]:
                check_activity(friend)

        if user_data['subscriptions']['users'] is not None:
            for user in user_data['subscriptions']['users'][:count[1]]:
                check_activity(user)

        if user_data['subscriptions']['groups'] is not None:
            for group in user_data['subscriptions']['groups'][:count[2]]:
                check_activity(group, is_groups=True)

        if times:
            post_dates = user_data['post_dates'] if user_data['post_dates'] is not None else []
            return self.convert_time(sorted(list(result) + post_dates))

        user_posts = self.__vk.wall.get(owner_id=user_data['id'], count=100)
        return list(result) + [(str(post['text']),
                                f'https://vk.com/wall{user_data["id"]}_{post["id"]}') for post in user_posts['items']]

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
