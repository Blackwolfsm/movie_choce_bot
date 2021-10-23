import os

from aiogram import Bot, types
from aiogram import Dispatcher
from aiogram.utils import executor
import dotenv

from utils_db import check_have_member, check_active, create_user, activated_user, deactivated_user
from templates import MESSAGES

dotenv.load_dotenv()
TOKEN = os.getenv('TOKEN_BOT')
ID_FOR_REPORT = 681108032

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


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


if __name__ == '__main__':
    executor.start_polling(dp)