import os
import random

from aiogram import Bot, types
from aiogram import Dispatcher
from aiogram.utils import executor
import dotenv


dotenv.load_dotenv()
TOKEN = os.getenv('TOKEN_BOT')

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


MESSAGE = {}
ID_BOT = 1361009578

@dp.message_handler(commands=['start'])
async def hello_from_start(message: types.Message):
    MESSAGE['new'] = message
    MESSAGE['1'] = await message.chat.get_member_count()
    MESSAGE['2'] = await message.chat.get_members_count()
    await message.reply(f'{MESSAGE["1"]}')


@dp.message_handler(commands=['roll'])
async def movie_choice(message: types.Message):
    administrators = await message.chat.get_administrators()
    # members = [user.username for user in administrators if user.username != 'blackwolf_assistant_bot']
    members = [member.user.first_name for member in administrators]
    watchers = list(members)
    members.remove('Жопосранчик')
    watchers.remove('Жопосранчик')
    not_unique = True
    while not_unique:
        not_unique = False
        random.shuffle(watchers)
        random.shuffle(members)
        for i in range(len(members)):
            if watchers[i] == members[i]:
                not_unique = True
    
    for i in range(len(members)):
        await message.reply(f'{members[i]} задает фильм для {watchers[i]}')
    



if __name__ == '__main__':
    executor.start_polling(dp)
