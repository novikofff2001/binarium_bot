import asyncio
import random

from log import log
#
import sys
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

# import settings
from config import TOKEN, WELCOME_MESSAGE
from user import Whitelist, USERS
from binarium import Binarium

# MAIN VARIABLES
# My ID is 971299290
token = TOKEN
bot = Bot(token)
dp = Dispatcher(bot)


@dp.message_handler(commands=['get_id'])
async def command_start(message):
    await bot.send_message(message.from_user.id, message.from_user.id)
    pass


@dp.message_handler(lambda message: message.from_user.id not in Whitelist.wl)
async def access_denied(message):
    await bot.send_message(message.from_user.id, "Access Denied!")
    log(access_denied.__name__, message.from_user.id, message.text)
    pass


#  LOGIN COMMANDS


@dp.message_handler(commands=['login'])
async def set_login(message):
    msg = str(message.text).replace('/login ', '')
    await bot.send_message(message.from_user.id, "Login: " + msg)
    USERS[message.from_user.id].login = msg
    pass


@dp.message_handler(commands=['pass'])
async def set_password(message):
    msg = str(message.text).replace('/pass ', '')
    USERS[message.from_user.id].password = msg
    USERS[message.from_user.id].dump()
    await bot.send_message(message.from_user.id, "Password: " + msg)
    pass


# CONNECT COMMANDS

@dp.message_handler(commands=['connect'])
async def command_connect(message):
    bm = Binarium()
    ans = "Connected successfully!"
    try:
        USERS[message.from_user.id].webdriver = bm.connect(
            login=USERS[message.from_user.id].login,
            password=USERS[message.from_user.id].password)
        USERS[message.from_user.id].connected = True
    except Exception as e:
        ans = e
    await bot.send_message(message.from_user.id, ans)
    pass

# Use below after connect !
from binarium import ALL_OPTIONS

@dp.message_handler(commands=['setoption'])
async def set_option(message):
    bm = Binarium()
    msg = str(message.text).replace('/setoption ', '')
    bm.set_option(USERS[message.from_user.id].webdriver, msg)
    print("Set {0}".format(msg))
    await bot.send_message(message.from_user.id, msg)

@dp.message_handler(commands=['closebanners'])
async def set_option(message):
    bm = Binarium()
    msg = str(message.text).replace('/closebanners ', '')
    bm.close_banners(USERS[message.from_user.id].webdriver)
    await bot.send_message(message.from_user.id, msg)

#

@dp.message_handler(commands=['wallet'])
async def set_wallet(message):
    bm = Binarium()
    msg = str(message.text).replace('/wallet ', '')
    choise = random.randint(0, 1)
    print("Set {}".format("Real" if choise else "Demo"))
    bm.change_wallet(USERS[message.from_user.id].webdriver, choise)
    await bot.send_message(message.from_user.id, msg)

#
@dp.message_handler(commands=['time'])
async def set_time(message):
    bm = Binarium()
    msg = str(message.text).replace('/time ', '')
    print("Set {}".format(msg))
    bm.set_time(USERS[message.from_user.id].webdriver, msg)
    await bot.send_message(message.from_user.id, msg)

##
@dp.message_handler(commands=['sum'])
async def set_time(message):
    bm = Binarium()
    msg = str(message.text).replace('/sum ', '')
    print("Set {}".format(msg))
    bm.set_bet_sum(USERS[message.from_user.id].webdriver, msg)
    await bot.send_message(message.from_user.id, msg)

#


@dp.message_handler(lambda message: message.from_user.id in USERS)
async def info_message(message):
    ans = "Login:" + USERS[message.from_user.id].login
    ans += "\nPass:" + USERS[message.from_user.id].password
    await bot.send_message(message.from_user.id, ans)
    pass



if __name__ == '__main__':
    executor.start_polling(dp)
