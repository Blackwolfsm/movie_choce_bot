import os

from aiogram import Bot, types
from aiogram import Dispatcher
from aiogram.utils import executor
from aiogram.utils.exceptions import BotBlocked, ChatNotFound
import dotenv

from utils_db import (check_have_member, check_active, create_roll, create_user, activated_user,
                      deactivated_user, count_active_members, get_ids_active_members,
                      make_purpose_rec, get_last_name, get_first_name,
                      get_ids_advisor_active_roll, get_id_watcher_from_advisor_last_roll,
                      get_ids_watchers_active_roll, get_id_advisor_from_wathcer_last_roll,
                      set_movie_for_purpose, set_state, get_state, reset_state, check_all_movie_assigned,
                      get_id_chanel_from_id_member, get_all_purposes, set_status_roll)
from utils import shuffle_members
from templates import MESSAGES

dotenv.load_dotenv()
TOKEN = os.getenv('TOKEN_BOT')
ID_FOR_REPORT = 681108032

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

movies_temp = dict()

@dp.message_handler(commands=['join'])
async def registration_user(message: types.Message):
    """Регистрация пользователя."""
    user = message.from_user
    try:
        if await check_bot_agree_for_user(user_id=user.id):
            if check_have_member(user.id):
                if check_active(user.id):
                    await message.reply(MESSAGES['is_reg_and_active'])
                else:
                    await message.reply(MESSAGES['is_reg_and_noactive'])
            else:
                if user.first_name and user.last_name:
                    create_user(id_member=user.id, 
                                first_name=user.first_name,
                                last_name=user.last_name,
                                id_chat=message.chat.id)
                    await message.reply(MESSAGES['reg_is_done'])
                else:
                    await message.reply(MESSAGES['not_first_or_last_name'])
        else:
            user_bot = await bot.get_me()
            nickname_bot = user_bot.username
            await message.reply(MESSAGES['reg_error_not_auth'].format(nickname_bot))
    except Exception as e:
        await bot.send_message(ID_FOR_REPORT, MESSAGES['report_error'].format(e))


@dp.message_handler(commands=['activate'])
async def activate_user(message: types.Message):
    """Активация зарегистрированного пользователя"""
    user = message.from_user
    try:
        if check_have_member(user.id):
            if check_active(user.id):
                await message.reply(MESSAGES['is_activate_was_active'])
            else:
                if await check_bot_agree_for_user(user_id=user.id):
                    activated_user(id_member=user.id)
                    await message.reply(MESSAGES['activate_is_done'])
                else:
                    user_bot = await bot.get_me()
                    nickname_bot = user_bot.username
                    await message.reply(MESSAGES['activate_error_not_auth'].format(nickname_bot))
        else:
            await message.reply(MESSAGES['not_reg'])
    except Exception as e:
        await bot.send_message(ID_FOR_REPORT, MESSAGES['report_error'].format(e))


@dp.message_handler(commands=['deactivate'])
async def deactivate_user(message: types.Message):
    """Деактивация зарегистрированного пользователя"""
    user = message.from_user
    try:
        if check_have_member(user.id):
            if check_active(user.id):
                deactivated_user(user.id)
                await message.reply(MESSAGES['is_deactivated_is_done'])
            else:
                await message.reply(MESSAGES['is_deactivated_was_deactive'])
        else:
            await message.reply(MESSAGES['not_reg'])
    except Exception as e:
        await bot.send_message(ID_FOR_REPORT, MESSAGES['report_error'].format(e))


@dp.message_handler(commands=['roll'])
async def roll_members(message: types.Message):
    """Назначает каждому участнику другого случайного участника"""
    count_member = count_active_members()
    if count_member > 1:
        id_roll = create_roll()
        links = shuffle_members(get_ids_active_members())
        for advisor_id, watcher_id in zip(links[0], links[1]):
            make_purpose_rec(id_advisor=int(advisor_id), id_watcher=int(watcher_id), id_roll=id_roll)
            set_state(id_member=advisor_id, status='find_movie')
            text_for_advisor = (f'Вы назначаете фильм для {get_first_name(watcher_id)} {get_last_name(watcher_id)}!'
                                f'Напишите фильм, который вы посоветуете для просмотра!')
            await bot.send_message(chat_id=advisor_id, text=text_for_advisor)
            
            await message.reply(f'{get_first_name(advisor_id)} {get_last_name(advisor_id)} '
                                f'задает фильм для {get_first_name(watcher_id)} {get_last_name(watcher_id)}')
    else:
        await message.reply(MESSAGES['roll_not_active'].format(count_member))


@dp.message_handler(lambda message: message.chat.id in get_ids_watchers_active_roll(), commands=['accept'])
async def accept_movie(message: types.Message):
    id_advisor = get_id_advisor_from_wathcer_last_roll(message.chat.id)
    if get_state(id_member=id_advisor) == 'send_movie':
        movie = movies_temp.pop(str(id_advisor))
        id_roll = set_movie_for_purpose(id_watcher=message.from_user.id,
                                title_movie=movie)
        reset_state(id_member=id_advisor)
        await message.reply('Приятного просмотра')
        await bot.send_message(chat_id=id_advisor,
                               text='Ваш фильм принят!')
        await check_all_assign(message=message, id_roll=id_roll)
    else:
        await message.reply('Для вас фильм еще не выбран!')    


@dp.message_handler(lambda message: message.chat.id in get_ids_watchers_active_roll(), commands=['decline'])
async def decline_movie(message: types.Message):
    id_advisor = get_id_advisor_from_wathcer_last_roll(message.chat.id)
    if get_state(id_member=id_advisor) == 'send_movie':
        movie = movies_temp.pop(str(id_advisor))
        set_state(id_member=id_advisor, status='find_movie')
        await message.reply('Хорошо, я скажу чтоб выбрали другой! :)')
        await bot.send_message(chat_id=id_advisor,
                                text='Ваш фильм не утвердили:( Выберите другой.')

    else:
        await message.reply('Для вас фильм еще не выбран!')   


@dp.message_handler(lambda message: message.chat.id in get_ids_advisor_active_roll(),
                    lambda message: get_state(message.chat.id) == 'find_movie')
async def question(message):
    movie = message.text
    movies_temp[str(message.from_user.id)] = movie
    set_state(id_member=message.from_user.id, status='check_movie')

    await message.reply(f'Твой фильм: {movie}.\n Да или Нет')


@dp.message_handler(lambda message: message.chat.id in get_ids_advisor_active_roll(),
                    lambda message: get_state(message.chat.id) == 'check_movie')
async def agree(message: types.Message):
    result = message.text
    if result.lower() == 'да':
        movie = movies_temp[str(message.from_user.id)]
        set_state(id_member=message.from_user.id, status='send_movie')
        await message.reply(f'Ваш фильм отправлен для согласования')
        id_watcher = get_id_watcher_from_advisor_last_roll(id_advisor=message.from_user.id)
        text_for_watcher = (
            f'{get_first_name(message.from_user.id)} {get_last_name(message.from_user.id)} '
            f'Советует вам фильм {movie}.\n Вы принимаете фильм?\n'
            f'Принять /accept \n Отказаться /decline'
        )
        await bot.send_message(
            chat_id=id_watcher,
            text=text_for_watcher
        )
    elif result.lower() == 'нет':
        set_state(id_member=message.from_user.id, status='find_movie')
        await message.reply(f'Жду фильм')


async def check_all_assign(message: types.Message, id_roll: int):
    """
    Проверка, всем ли участникам ролла заданы фильмы. В случае успеха,
    отправляется в канал все назначения.
    """
    if check_all_movie_assigned():
        id_chanel = get_id_chanel_from_id_member(message.from_user.id)
        await bot.send_message(id_chanel, MESSAGES['roll_done'])
        all_assigns = get_all_purposes(id_roll=id_roll)
        for assign in all_assigns:
            await bot.send_message(id_chanel, MESSAGES['roll_done_item'].format(
                ' '.join(assign[:2]), 
                ' '.join(assign[2:4]), 
                assign[4]
                )
            )
        set_status_roll(id_roll=id_roll, id_status=1)
    else:
        pass


async def check_bot_agree_for_user(user_id: int) -> bool:
    '''
    Проверяет возможность отправки пользователю сообщений.
    '''
    try:
        message = await bot.send_message(chat_id=user_id, 
                                         text='Бип-Бип проверка')
        await bot.delete_message(chat_id=user_id, 
                                 message_id=message.message_id)
        return True
    except (BotBlocked, ChatNotFound):
        return False


if __name__ == '__main__':
    executor.start_polling(dp)
