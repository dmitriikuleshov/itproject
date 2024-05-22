"""Класс, отвечающий за доступ к VK API"""

from typing import List, Optional, Tuple, Dict
from json import dump, load
from random import shuffle
from datetime import datetime
from time import time
import re

import vk_api
from vk_api.exceptions import ApiError

from .toxicity_check import check_obscene_vocabulary
from .gigachat_tools import check_acquaintances, get_written_squeeze
from .vk_tools_models import UserInfo, University, Subscriptions, GroupInfo


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
    get_mutual_friends(*links)
        Получение информации об общих друзьях нескольких пользователей
    get_common_connections(link)
        Получение информации о друзьях пользователя и связях между ними
    analyse_acquaintances(user_info, count, country, city)
        Поиск потенциальных знакомств для данного пользователя
    __dump_big_users_data(k)
        Генерация локальной базы аккаунтов ВК для анализа на знакомства

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

    def get_id_from_link(self, link: str) -> int:
        """
        Метод, возвращающий ID пользователя по ссылке на его профиль

        Parameters
        ----------
        link: str
            Ссылка на анализируемый аккаунт VK

        Returns
        -------
        int
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
                    user_id = int(resolved_name['object_id']) if resolved_name['type'] == 'user' else None
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
        raw_dict = self.__vk.users.get(user_id=_id, fields='first_name, last_name, bdate, '
                                                           'country, city, activities, '
                                                           'books, education, games, '
                                                           'interests, movies, music, personal, '
                                                           'counters, photo_50')[0]

        try:
            friends = self.__vk.friends.get(user_id=_id, order='hints')['items']
            subs = self.__vk.users.getSubscriptions(user_id=_id)
            sub_users = subs['users']['items']
            sub_groups = subs['groups']['items']
            posts = [post['date'] for post in self.__vk.wall.get(owner_id=_id, count=100)['items']]
        except ApiError:
            friends = sub_users = sub_groups = posts = None

        user_university = University(
            name=raw_dict.get('university_name'),
            faculty=raw_dict.get('faculty_name'),
            form=raw_dict.get('education_form'),
            graduation=raw_dict.get('graduation')
        )

        user_subscriptions = Subscriptions(
            users=sub_users,
            groups=sub_groups
        )

        user_info = UserInfo(
            id=_id,
            first_name=raw_dict.get('first_name'),
            last_name=raw_dict.get('last_name'),
            birthday=raw_dict.get('bdate'),
            country=raw_dict['country']['title'] if 'country' in raw_dict.keys() else None,
            city=raw_dict['city']['title'] if 'city' in raw_dict.keys() else None,
            interests=raw_dict.get('interests'),
            books=raw_dict.get('books'),
            games=raw_dict.get('games'),
            movies=raw_dict.get('movies'),
            activities=raw_dict.get('activities'),
            music=raw_dict.get('music'),
            university=user_university,
            friends_count=raw_dict['counters'].get('friends'),
            followers_count=raw_dict['counters'].get('followers'),
            friends=friends,
            subscriptions=user_subscriptions,
            post_dates=posts,
            icon=raw_dict.get('photo_50')
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
            id=_id,
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
        if not users_ids_list:
            return []

        raw = self.__vk.users.get(user_ids=users_ids_list, fields='first_name, last_name, photo_50')
        list_of_user_info = []

        for raw_user in raw:
            list_of_user_info.append(UserInfo(
                id=raw_user['id'],
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
        if not groups_ids_list:
            return []
        raw = self.__vk.groups.getById(group_ids=groups_ids_list)
        list_of_group_info = []

        for group in raw:
            list_of_group_info.append(GroupInfo(
                id=group.get('id'),
                name=group.get('name'),
                link=f'https://vk.com/{group["screen_name"]}' if 'screen_name' in group.keys() else None,
                photo=group.get('photo_50')
            ))

        return list_of_group_info

    def get_activity(self, user_data: UserInfo, count: Tuple[int] = (5, 5, 5), time_limit: int = 2629743,
                     times: bool = True) -> List[str] | List[Tuple[str, str]] | None:
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
        List[str] | List[Tuple[str]] | None
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

        try:
            posts = self.__vk.wall.get(owner_id=user_data['id'], count=100)

            return list(result) + [(post['text'],
                                    f'https://vk.com/wall{user_data["id"]}_{post["id"]}') for post in posts['items']]
        except ApiError:
            return

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

    def get_mutual_friends(self, *links: Tuple[str] | str) -> List[UserInfo] | None:
        """
        Метод, принимающий кортеж ссылок на пользователей и возвращающий
        List[UserInfo] - список информации об общих друзьях (UserInfo) для переданных ссылок.
        В случае ошибки при получении информации о друзьях для одного из пользователей,
        возвращает None (если профиль скрыт)

        Parameters
        ----------
        links: Tuple[str] | str
            Ссылки на пользователей

        Returns
        -------
        List[UserInfo] | None
            Список объектов данных о пользователях\

        """
        _ids = [self.get_id_from_link(link) for link in links]
        _friends_sets = []

        for _id in _ids:
            try:
                friends = set(self.__vk.friends.get(user_id=_id, count=20)['items'])
                _friends_sets.append(friends)
            except ApiError:
                return

        mutual_friends = set.intersection(*_friends_sets)
        return self.get_users_list_info(list(mutual_friends))

    def get_common_connections(self, link: str) -> List[Tuple[UserInfo, Optional[List[UserInfo]]]] | None:
        """
        Метод, принимающий ссылку на пользователя
        и возвращающий список кортежей, где каждый кортеж содержит
        информацию о друге пользователя и список их общих друзей с переданным пользователем.

        Parameters
        ----------
        link: str
            Ссылка на аккаунт

        Returns
        -------
        List[Tuple[UserInfo, Optional[List[UserInfo]]]] | None
            Список кортежей с информацией о связях между аккаунтами

        """
        try:
            _id = self.get_id_from_link(link)
            _friends = self.__vk.friends.get(user_id=_id, count=20)['items']
            connections = []

            for friend in self.get_users_list_info(_friends):
                connections.append(
                    (friend, self.get_mutual_friends(link, str(friend.get('id'))))
                )

            return connections
        except ApiError:
            return

    @staticmethod
    def analyse_acquaintances(user_info: UserInfo, count: int = 10, country: bool = True,
                              city: bool = True) -> List[Dict[str, str]]:
        """
        Метод, принимающий данные о пользователе, и возвращающий
        список данных пользователей, рекомендуемых GigaChat для знакомства

        Parameters
        ----------
        user_info: UserInfo
            Данные о пользователе
        count: int
            Максимальное число пользователей в возвращаемом списке
        country: bool
            Нужно ли учитывать совпадение страны пользователя и рекомендуемого аккаунта?
        city: bool
            Нужно ли учитывать совпадение города пользователя и рекомендуемого аккаунта?

        Returns
        -------
        List[Dict[str, str]]
            Список словарей с короткой информацией о рекомендуемом аккаунте

        """
        with open('vkapi/data.json') as f:
            data = load(f)

        filter_data, result_data = [], []

        if country or city:
            for user in data:
                if ((not country or (user_info['country'] is not None and
                                     user_info['country'].lower() == user['country']['title'].lower())
                     and (not city or (user_info['city'] is not None and
                                       user_info['city'].lower() == user['city']['title'].lower())))) or (
                        (country and user_info['country'] is None) or (city and user_info['city'] is None)
                ):
                    filter_data.append(user)

        check = set()
        shuffle(filter_data)
        written_squeeze = get_written_squeeze(user_info)

        for user in filter_data:
            if check_acquaintances(
                    first_user_interest=written_squeeze,
                    second_user_interest=user['interests']
            ) and user['id'] != user_info['id'] and user['id'] not in check:
                result_data.append({
                    'first_name': user.get('first_name'),
                    'last_name': user.get('last_name'),
                    'interests': user.get('interests'),
                    'link': f'https://vk.com/id{user["id"]}',
                    'icon': user.get('photo_50')
                })
                check.add(user['id'])
                if len(result_data) == count:
                    break

        return result_data

    def __dump_big_users_data(self, k: int) -> None:
        """
        Служебный метод для обновления базы данных аккаунтов вк
        для последующего анализа на знакомства. За раз
        записывает данный аккаунтов с ID от k * 1000 до k * 1000 + 5000

        Parameters
        ----------
        k: int
            Параметр границ рассматриваемых ID

        """
        ind = [str([j for j in range(j, j + 1000)])[1:-1] for j in range(10000 + k * 1000, 15000 + k * 1000, 1000)]
        res_code = ''.join([f'var {"a" * (i + 1)} = API.users.get({{"user_ids":"{ind[i]}", '
                            f'"fields": "city, country, interests"}});' for i in range(len(ind))])
        rs_vars = ''.join([f'{"a" * (i + 1)}+' for i in range(len(ind))])[:-1]

        data = self.__vk.execute(code=f'{res_code}return {rs_vars};')

        with open('data.json') as f:
            _json = load(f)

        for el in data:
            if 'country' in el.keys() and 'interests' in el.keys():
                if el['interests']:
                    _json.append(el)

        with open('data.json', 'w') as f:
            dump(_json, f, indent=4)
