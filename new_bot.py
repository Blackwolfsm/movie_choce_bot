import os

from aiogram import Bot, types
from aiogram import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import dotenv

from utils_db import (check_have_member, check_active, create_roll, create_user, activated_user,
                      deactivated_user, count_active_members, get_ids_active_members,
                      make_purpose_rec, get_last_name, get_first_name,
                      get_ids_advisor_active_roll, get_id_watcher_from_advisor_last_roll,
                      get_ids_watchers_active_roll, get_id_advisor_from_wathcer_last_roll,
                      set_movie_for_purpose)
from utils import shuffle_members, AdvisorStates, generate_markup_keybord
from templates import MESSAGES

dotenv.load_dotenv()
TOKEN = os.getenv('TOKEN_BOT')
ID_FOR_REPORT = 681108032

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

movies_temp = dict()


@dp.message_handler(commands=['join'])
async def registration_user(message: types.Message):
    """Регистрация пользователя."""
    user = message.from_user
    try:
        if check_have_member(user.id):
            if check_active(user.id):
                await message.reply(MESSAGES['is_reg_and_active'])
            else:
                await message.reply(MESSAGES['is_reg_and_noactive'])
        else:
            if user.first_name and user.last_name:
                create_user(user.id, user.first_name, user.last_name)
                await message.reply(MESSAGES['reg_is_done'])

            else:
                await message.reply(MESSAGES['not_first_or_last_name'])
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
                activated_user(id_member=user.id)
                await message.reply(MESSAGES['activate_is_done'])
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
            state = dp.current_state(user=advisor_id)
            await state.set_state(AdvisorStates.FIND_MOVIE[0])
            text_for_advisor = (f'Вы назначаете фильм для {get_first_name(watcher_id)} {get_last_name(watcher_id)}!')
            markup = generate_markup_keybord(['/ready'])
            await bot.send_message(chat_id=advisor_id, text=text_for_advisor, reply_markup=markup)
            
            await message.reply(f'{get_first_name(advisor_id)} {get_last_name(advisor_id)} '
                                f'задает фильм для {get_first_name(watcher_id)} {get_last_name(watcher_id)}')
    else:
        await message.reply(MESSAGES['roll_not_active'].format(count_member))


@dp.message_handler(commands=['ready'])
async def ready_for_advisor(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(AdvisorStates.FIND_MOVIE[0])
    await message.reply(text='Напишите фильм, который вы посоветуете для просмотра!', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(lambda message: message.chat.id in get_ids_watchers_active_roll(), commands=['accept'])
async def accept_movie(message: types.Message):
    id_advisor = get_id_advisor_from_wathcer_last_roll(message.chat.id)
    state_advisor = dp.current_state(user=id_advisor)
    if await state_advisor.get_state() == 'send_movie':
        movie = movies_temp.pop(str(id_advisor))
        set_movie_for_purpose(id_watcher=message.from_user.id,
                                title_movie=movie)
        await state_advisor.reset_state()
        await message.reply('Приятного просмотра')
        await bot.send_message(chat_id=id_advisor,
                                text='Ваш фильм принят!')
    else:
        await message.reply('Для вас фильм еще не выбран!')    


@dp.message_handler(lambda message: message.chat.id in get_ids_watchers_active_roll(), commands=['decline'])
async def decline_movie(message: types.Message):
    id_advisor = get_id_advisor_from_wathcer_last_roll(message.chat.id)
    state_advisor = dp.current_state(user=id_advisor)
    if await state_advisor.get_state() == 'send_movie':
        movie = movies_temp.pop(str(id_advisor))
        state = dp.current_state(user=id_advisor)
        await state.set_state(AdvisorStates.FIND_MOVIE[0])
        await message.reply('Хорошо, я скажу чтоб выбрали другой! :)')
        await bot.send_message(chat_id=id_advisor,
                                text='Ваш фильм не утвердили:( Выберите и напишите другой.')

    else:
        await message.reply('Для вас фильм еще не выбран!')   


@dp.message_handler(lambda message: message.chat.id in get_ids_advisor_active_roll(), state=AdvisorStates.FIND_MOVIE)
async def question(message):
    movie = message.text
    state_advisor = dp.current_state(user=message.from_user.id)
    movies_temp[str(message.from_user.id)] = movie
    await state_advisor.set_state(AdvisorStates.CHECK_MOVIE[0])

    await message.reply(f'Твой фильм: {movie}.\n Да или Нет')


@dp.message_handler(lambda message: message.chat.id in get_ids_advisor_active_roll(), state=AdvisorStates.CHECK_MOVIE)
async def agree(message: types.Message):
    result = message.text
    state_advisor = dp.current_state(user=message.from_user.id)
    if result.lower() == 'да':
        movie = movies_temp[str(message.from_user.id)]
        await state_advisor.set_state(AdvisorStates.SEND_MOVIE[0])
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
        await state_advisor.set_state(AdvisorStates.FIND_MOVIE[0])
        await message.reply(f'Жду фильм')


if __name__ == '__main__':
    executor.start_polling(dp)