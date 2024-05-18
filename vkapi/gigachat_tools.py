from gigachat import GigaChat
import os


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
        response = giga.chat(f'Тебе дано описание интересов пользователя соцсети: \'{first_user_interest}\'. Ответь ДА,'
                             ' если, по твоему мнению, этому пользователю будет интересно общаться с пользователем с '
                             f'такими интересами: \'{second_user_interest}\', иначе ответь НЕТ.')
        return response.choices[0].message.content == 'ДА'
