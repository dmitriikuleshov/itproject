from requests import get
from typing import List


def check_obscene_vocabulary(data: List[str]) -> List[str]:
    """
    Проверка списка входящих строк на предмет наличия нецензурной
    или оскорбительной лексики по онлайн-базе. Возврат списка тех
    строк, в которых она была найдена
    :param data: List[str]
    :return: List[str]
    """
    dictionary = get(
        'https://raw.githubusercontent.com/odaykhovskaya/obscene_words_ru/master/obscene_corpus.txt'
    ).text.lower().split('\n')[:-1]

    all_texts = ''.join(data).lower()

    for char in all_texts:
        if not char.isalpha():
            all_texts = all_texts.replace(char, ' ')

    finds, result = [], []

    for word in dictionary:
        if f' {word} ' in all_texts:
            finds.append(word)

    for elem in data:
        for word in finds:
            if word in elem.lower():
                temp = elem.lower()

                for char in temp:
                    if not char.isalpha():
                        temp = temp.replace(char, ' ')

                if word in temp:
                    result.append(elem)
                    break

    return result
