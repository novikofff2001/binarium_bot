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
from binarium import Binarium, autobet_inspector, prepare_info_message, prepare_bets_message

# MAIN VARIABLES
# My ID is 971299290
token = TOKEN
bot = Bot(token)
dp = Dispatcher(bot)


@dp.message_handler(commands=['autobet_sum'])
async def set_autobet_sum(message):
    msg = str(message.text).replace('/autobet_sum', '').replace(' ', '')
    try:
        float(msg)
        USERS[message.from_user.id].autobet_params['bet_sum'] = msg
        msg = "Set Autobet sum: {0}".format(msg)
    except ValueError:
        msg = "Input correct value(ex. 60.0, 120) and try again"
    await bot.send_message(message.from_user.id, msg)
    pass


@dp.message_handler(commands=['autobet_wallet'])
async def set_autobet_wallet(message):
    user_id = message.from_user.id
    wallet = USERS[user_id].autobet_params['real_wallet']
    USERS[user_id].autobet_params['real_wallet'] = not wallet
    await bot.send_message(message.from_user.id, "Choosed {0} wallet".format(
        "Real" if USERS[user_id].autobet_params['real_wallet']
        else "Demo"))
    pass


@dp.message_handler(commands=['autobet'])
async def command_autobet(message):
    msg = str(message.text).replace('/autobet ', '')
    data = msg.split()
    option = exp_time = direction = str()
    bm = Binarium()
    for elem in data:
        if bm.is_option(elem):
            option = elem
        elif bm.is_time(elem):
            exp_time = elem
        elif bm.is_direction(elem):
            direction = elem
    print(option, exp_time, direction)
    if option and exp_time and direction:
        bm.add_autobet(message.from_user.id, option, exp_time, direction)
    await bot.send_message(message.from_user.id, msg)
    pass


@dp.message_handler(commands=['get_id'])
async def command_get_id(message):
    log(command_get_id.__name__, message.from_user.id, "Sent request")
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
    msg = str(message.text).replace('/login', '').replace(' ', '')
    if msg:
        USERS[message.from_user.id].login = msg
    await bot.send_message(message.from_user.id, "Login: {0}".format(msg) if msg else "Forgot login...")
    pass


@dp.message_handler(commands=['pass'])
async def set_password(message):
    msg = str(message.text).replace('/pass', '').replace(' ', '')
    USERS[message.from_user.id].password = msg
    if len(USERS[message.from_user.id].login) > 0 and len(USERS[message.from_user.id].password) > 0:
        USERS[message.from_user.id].dump()
    await bot.send_message(message.from_user.id, "Password: {0}".format(msg) if msg else "Forgot pass...")
    pass


# CONNECT COMMANDS

@dp.message_handler(commands=['connect'])
async def command_connect(message):
    bm = Binarium()
    ans = "Connected successfully!"
    try:
        USERS[message.from_user.id].connected = bm.connect(message.from_user.id)
    except Exception as e:
        ans = e
    await bot.send_message(message.from_user.id, ans)
    pass


@dp.message_handler(lambda message: not USERS[message.from_user.id].connected)
async def info_message(message):
    ans = ''
    if USERS[message.from_user.id].login:
        ans += "Login:" + USERS[message.from_user.id].login
    if USERS[message.from_user.id].password:
        ans += "\nPass:" + USERS[message.from_user.id].password
    await bot.send_message(message.from_user.id, ans if len(ans) > 0 else "Input /login <login> and /pass <pass>")
    pass


@dp.message_handler(commands=['setoption'])
async def set_option(message):
    bm = Binarium()
    msg = str(message.text).replace('/setoption ', '')
    bm.set_option(USERS[message.from_user.id].webdriver, msg)
    print("Set {0}".format(msg))
    await bot.send_message(message.from_user.id, msg)
    pass


@dp.message_handler(commands=['closebanners'])
async def close_banners(message):
    bm = Binarium()
    msg = str(message.text).replace('/closebanners ', '')
    bm.close_banners(USERS[message.from_user.id].webdriver)
    await bot.send_message(message.from_user.id, msg)
    pass


#

@dp.message_handler(commands=['wallet'])
async def set_wallet(message):
    bm = Binarium()
    msg = str(message.text).replace('/wallet ', '')
    choise = random.randint(0, 1)
    print("Set {}".format("Real" if choise else "Demo"))
    bm.change_wallet(USERS[message.from_user.id].webdriver, choise)
    await bot.send_message(message.from_user.id, msg)
    pass


#
@dp.message_handler(commands=['time'])
async def set_time(message):
    bm = Binarium()
    msg = str(message.text).replace('/time ', '')
    print("Set {}".format(msg))
    bm.set_time(USERS[message.from_user.id].webdriver, msg)
    await bot.send_message(message.from_user.id, msg)
    pass


##
@dp.message_handler(commands=['sum'])
async def set_sum(message):
    bm = Binarium()
    msg = str(message.text).replace('/sum ', '')
    print("Set {}".format(msg))
    bm.set_bet_sum(USERS[message.from_user.id].webdriver, msg)
    await bot.send_message(message.from_user.id, msg)
    pass


##
@dp.message_handler(commands=['bet'])
async def do_bet(message):
    bm = Binarium()
    msg = str(message.text).replace('/bet ', '')
    bm.bet(USERS[message.from_user.id].webdriver, msg)
    print("Bet {0}".format(msg))
    await bot.send_message(message.from_user.id, "Bet {0}".format(msg))
    pass


@dp.message_handler(commands=['get_info'])
async def set_info(message):
    bm = Binarium()
    msg = prepare_info_message(bm.collect_info(USERS[message.from_user.id].webdriver))
    await bot.send_message(message.from_user.id, msg)
    pass


@dp.message_handler(commands=['active_bets'])
async def get_active_bets(message):
    bm = Binarium()
    msg = prepare_bets_message(bm.get_active_bets(USERS[message.from_user.id].webdriver))
    await bot.send_message(message.from_user.id, msg)
    pass


if __name__ == '__main__':
    asyncio.get_event_loop().create_task(autobet_inspector(bot))
    executor.start_polling(dp, skip_updates=True)
