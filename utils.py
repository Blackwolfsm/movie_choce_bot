import random

from aiogram.utils.helper import Helper, HelperMode, ListItem


class AdvisorStates(Helper):
    """Класс состояний для участника в роли задающего фильм"""
    mode = HelperMode.snake_case

    FIND_MOVIE = ListItem()
    CHECK_MOVIE = ListItem()
    SEND_MOVIE = ListItem()


def shuffle_members(list_id_members: list) -> list:
    """Принимает список участников, возвращает связи участников случайным образом"""
    advisor = list_id_members
    watchers = list(advisor)
    unique = False
    while not unique:
        unique = True
        random.shuffle(advisor)
        random.shuffle(watchers)
        for i in range(len(advisor)):
            if advisor[i] == watchers[i]:
                unique = False

    result = [advisor, watchers]
    return result

