import os

from aiogram import Bot, types
from aiogram import Dispatcher
from aiogram.utils import executor
import dotenv


dotenv.load_dotenv()
TOKEN = os.getenv('TOKEN_BOT')

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def hello_from_start(messsage: types.Message):
    await messsage.reply('Привет')

if __name__ == '__main__':
    executor.start_polling(dp)
