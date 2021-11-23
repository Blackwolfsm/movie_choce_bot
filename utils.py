import random
import os

from aiogram import types
from amzqr import amzqr


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


def generate_qr(path_to_img: str, words: str, id: int):
    """
    Принимает путь к картинке и слова для генерации QR кода, 
    а так же id для присваивания имени новому файлу. Возвращает 
    путь с именем файла после генерации.
    """
    path_to_file = os.getcwd() + os.sep + 'files'
    filename = f'qr_code_{id}.png'
    version, level, qr_name = amzqr.run(
        words = words,
        version=1,
        level='H',
        picture=path_to_img,
        colorized=True,
        contrast=1.0,
        brightness=1.0,
        save_name=filename,
        save_dir=path_to_file
    )
    return qr_name
