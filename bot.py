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
from user import Whitelist, USERS, USER_INFO_TEMPLATE, ACTIVE_BET_TEMPLATE
from binarium import Binarium

# MAIN VARIABLES
# My ID is 971299290
token = TOKEN
bot = Bot(token)
dp = Dispatcher(bot)


def prepare_info_message(result):
    msg = '=' * 30 + '\n'
    msg += "money:{0}\n".format(result['money'])
    msg += "real_wallet:{0}\n".format(result['real_wallet'])
    msg += "bet_sum:{0}\n".format(result['bet_sum'])
    msg += "profit_perсents:{0}\n".format(result['profit_perсents'])
    msg += "profit_sum:{0}\n".format(result['profit_sum'])
    msg += "time:{0}\n".format(result['time'])
    if len(msg) == 0:
        msg = 'No Info'
    return msg


def prepare_bets_message(result):
    msg = ''
    bet_num = int(0)
    for key in result.keys():
        print(key, result[key])
        bet_num += 1
        msg += '{:=^30}\n'.format("Active bet №{0}".format(bet_num))
        msg += 'Option: {0}\n'.format(result[key]['option'])
        msg += 'expiration time: {0}\n'.format(result[key]['timer'])
        msg += 'Sum of bet: {0}\n'.format(result[key]['profit_perсents'])
        msg += 'Profit sum: {0}\n'.format(result[key]['profit_sum'])
        msg += 'Profit percents: {0}\n'.format(result[key]['profit_perсents'])
    if len(msg) == 0:
        msg = 'No Active bets'
    return msg


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
    up = msg.lower().find('верх') != -1 and msg.lower().find('вниз') == -1
    print("Bet {0}".format("Up" if up else "Down"))
    bm.bet(USERS[message.from_user.id].webdriver, up)
    await bot.send_message(message.from_user.id, msg)
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


@dp.message_handler(lambda message: message.from_user.id in USERS)
async def info_message(message):
    ans = ''
    if USERS[message.from_user.id].login:
        ans += "Login:" + USERS[message.from_user.id].login
    if USERS[message.from_user.id].password:
        ans += "\nPass:" + USERS[message.from_user.id].password
    await bot.send_message(message.from_user.id, ans if len(ans) > 0 else "Input /login and /pass")
    pass


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
