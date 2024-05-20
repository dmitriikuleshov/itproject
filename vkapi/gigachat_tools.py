"""Функции работы с API GigaChat"""

import os

from gigachat import GigaChat

from .vk_tools_models import UserInfo


def check_acquaintances(first_user_interest: str, second_user_interest: str) -> bool:
    """
    Функция принимает строки с описанием интересов двух пользователей
    и возвращает True, если, по мнению GigaChat, им будет интересно общаться

    Parameters
    ----------
    first_user_interest: str
        Интересы первого пользователя
    second_user_interest: str
        интересы второго пользователя

    Returns
    -------
    bool
        Будет ли интересно общаться пользователям?

    """
    with GigaChat(credentials=os.environ['GIGACHAT_TOKEN'], verify_ssl_certs=False) as giga:
        response = giga.chat(f'Тебе дано описание пользователя соцсети: \'{first_user_interest}\'. Ответь ДА,'
                             ' если, по твоему мнению, этому пользователю будет интересно общаться с пользователем с '
                             f'такими интересами: \'{second_user_interest}\', иначе ответь НЕТ. Также, если интересы '
                             f'второго пользователя слишком размытые, общие и не конкретные, тоже ответь НЕТ.')
    return response.choices[0].message.content == 'ДА'


def get_written_squeeze(i: UserInfo) -> str:
    """
    Функция, принимающая краткую информацию о пользователе
    и возвращающая текстовую выжимку из неё со слов GigaChat

    Parameters
    ----------
    i: UserInfo
        Информация о пользователе

    Returns
    -------
    str
        Текстовая выжимка

    """
    prompt = 'Тебе дано следующее описание пользователя Вконтакте: \''

    if i['first_name'] or i['last_name']:
        prompt += (f'Пользователя зовут {i["first_name"] if i["first_name"] else ""}'
                   f'{" " + i["last_name"] if i["last_name"] else ""}. ')

    if i['birthday']:
        prompt += f'Он родился {i["birthday"]}. '

    if i['country'] or i['city']:
        if i['country']:
            prompt += f'Страна пользователя: {i["country"]}. '
        if i['city']:
            prompt += f'Город пользователя: {i["city"]}. '

    if i['interests']:
        prompt += f'У него есть следующие интересы: "{i["interests"]}". '
    if i['books']:
        prompt += f'Ему нравятся книги: {i["books"]}. '
    if i['games']:
        prompt += f'Ему нравятся игры: {i["games"]}. '
    if i['movies']:
        prompt += f'Ему нравятся фильмы: {i["movies"]}. '
    if i['activities']:
        prompt += f'Он увлекается {i["activities"]}. '
    if i['music']:
        prompt += f'Ему нравится музыка: {i["music"]}. '

    if i['university']:
        if i['university']['name']:
            prompt += f'Место получения им высшего образования - {i["university"]["name"]}.'
        if i['university']['faculty']:
            prompt += f'Он обучается на факультете {i["university"]["faculty"]}'
        if i['university']['form']:
            prompt += f'Он обучается по форме обучения - {i["university"]["form"]}]'
        if i['university']['graduation']:
            prompt += f'Он закончил образование в {i["university"]["graduation"]} году'
        prompt += '. '

    if i['friends_count']:
        prompt += f'У него {i["friends_count"]} друзей. '
    if i['followers_count']:
        prompt += f'У него {i["followers_count"]} подписчиков. '

    prompt += ('\'. На основании этой информации составь краткое описание пользователя, ИСПОЛЬЗУЯ ТОЛЬКО '
               'УКАЗАННУЮ В ЭТОМ ЗАПРОСЕ ИНФОРМАЦИЮ, НЕ ИСПОЛЬЗУЮ ДРУГИЕ ФАКТЫ, НЕ ДЕЛАЙ ОЦЕНОЧНЫХ СУБЪЕКТИВНЫХ '
               'СУЖДЕНИЙ, в описании СОБЛЮДАЙ правила русского языка. В ответ отправь ТОЛЬКО получившийся рассказ.')

    with GigaChat(credentials=os.environ['GIGACHAT_TOKEN'], verify_ssl_certs=False) as giga:
        response = giga.chat(prompt)

    return response.choices[0].message.content
