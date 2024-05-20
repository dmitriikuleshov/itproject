"""Функция анализа текстов на наличие нецензурной лексики"""

from typing import List, Tuple, Optional

from requests import get


def check_obscene_vocabulary(data: List[Tuple[str, str]]) -> List[Optional[str]]:
    """
    Проверка списка входящих строк на предмет наличия нецензурной
    или оскорбительной лексики по онлайн-базе. Возврат ссылок на посты,
    в которых она была найдена

    Parameters
    ----------
    data: List[Tuple[str]]
        Список текстов постов и ссылок на них

    Returns
    -------
    List[Optional[str]]
        Список со ссылками на тексты с нецензурной лексикой

    """
    dictionary = get(
        'https://raw.githubusercontent.com/odaykhovskaya/obscene_words_ru/master/obscene_corpus.txt'
    ).text.lower().split('\n')[:-1]

    all_texts = ' ' + ''.join([elem[0] for elem in data]).lower() + ' '

    for char in all_texts:
        if not char.isalpha():
            all_texts = all_texts.replace(char, ' ')

    finds, result = [], []

    for word in dictionary:
        if f' {word} ' in all_texts:
            finds.append(word)

    for elem in data:
        for word in finds:
            if word in elem[0].lower():
                temp = elem[0].lower()

                for char in temp:
                    if not char.isalpha():
                        temp = temp.replace(char, ' ')

                if word in temp:
                    result.append(elem[1])
                    break

    return result
