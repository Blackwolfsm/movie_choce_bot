import random

from aiogram import types


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


def generate_markup_keybord(buttons: list) -> types.ReplyKeyboardMarkup:
    """
    Генерирует клавиатуру.
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    for but in buttons:
        markup.add(but)

    return markup
