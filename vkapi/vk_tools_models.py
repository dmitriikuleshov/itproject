"""Модели словарей, связанных с информацией об аккаунтах ВК"""

from typing import TypedDict, Optional, List


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
        Год выпуска

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
