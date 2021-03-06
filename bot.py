# -*- coding: utf-8 -*-
import asyncio
import random

from log import log
#
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

# import settings
from config import TOKEN, WELCOME_MESSAGE
from user import Whitelist, User, USERS
from binarium import Binarium, autobet_inspector, prepare_info_message, prepare_bets_message

# MAIN VARIABLES
# My ID is 971299290
token = TOKEN
bot = Bot(token)
dp = Dispatcher(bot)
for user_id in Whitelist().wl:
    USERS[user_id] = User(user_id)


@dp.message_handler(commands=['get_id'])
async def command_get_id(message):
    log(command_get_id.__name__, message.from_user.id, "Sent request")
    await bot.send_message(message.from_user.id, message.from_user.id)
    pass


@dp.message_handler(lambda message: message.from_user.id not in USERS)
async def access_denied(message):
    if message.from_user.id in Whitelist().wl:
        await command_start(message)
    else:
        await bot.send_message(message.from_user.id, "Access Denied! send /get_id to make request to admin")
        log(access_denied.__name__, message.from_user.id, message.text)
    pass


@dp.message_handler(commands=['start'])
async def command_start(message):
    ans = WELCOME_MESSAGE
    USERS[message.from_user.id] = User(message.from_user.id)
    await bot.send_message(message.from_user.id, ans)
    log(command_start.__name__, message.from_user.id, message.text)
    pass


@dp.message_handler(commands=['get_login_info'])
async def command_get_login_info(message):
    ans = ''
    if USERS[message.from_user.id].login:
        ans += "Login: " + USERS[message.from_user.id].login
    if USERS[message.from_user.id].password:
        ans += "\nPass: " + USERS[message.from_user.id].password
    if USERS[message.from_user.id].autobet['sum']:
        ans += "\nAutobet Sum: " + USERS[message.from_user.id].autobet['sum']
    ans += "\nWallet: {0}".format("Real" if USERS[message.from_user.id].autobet['real_wallet'] else "Demo")
    if USERS[message.from_user.id].login and USERS[message.from_user.id].password:
        ans += "\n/connect"
    else:
        ans += "\nInput /login <login> and /pass <pass>"
    await bot.send_message(message.from_user.id, ans)
    log(command_get_login_info.__name__, message.from_user.id, "Got Login Info")
    pass


@dp.message_handler(commands=['autobet_sum'])
async def set_autobet_sum(message):
    msg = str(message.text).replace('/autobet_sum', '').replace(' ', '')
    try:
        float(msg)
        USERS[message.from_user.id].autobet['sum'] = msg
        USERS[message.from_user.id].dump()
        msg = "Set Autobet sum: {0}".format(msg)
    except ValueError:
        msg = "Input correct value(ex. 60.0, 120) and try again"
    await bot.send_message(message.from_user.id, msg)
    log(set_autobet_sum.__name__, message.from_user.id, msg)
    pass


@dp.message_handler(commands=['autobet_wallet'])
async def set_autobet_wallet(message):
    wallet = USERS[message.from_user.id].autobet['real_wallet']
    USERS[message.from_user.id].autobet['real_wallet'] = not wallet
    ans = "Choosed {} wallet".format("Real" if USERS[message.from_user.id].autobet['real_wallet'] else "Demo")
    await bot.send_message(message.from_user.id, ans)
    log(set_autobet_wallet.__name__, message.from_user.id, ans)
    USERS[message.from_user.id].dump()
    pass


@dp.message_handler(commands=['autobet'])
async def command_autobet(message):
    msg = str(message.text).replace('/autobet ', '')
    data = msg.split()
    option = exp_time = direction = str()
    bm = Binarium()
    for elem in data:
        if bm.is_option(elem):
            option = elem.upper()
        elif bm.is_time(elem):
            exp_time = elem
        elif bm.is_direction(elem):
            direction = elem
    if option and exp_time and direction:
        bm.add_autobet(message.from_user.id, option, exp_time, direction)
        msg = "Autobet received: {}, {}, {}".format(option, exp_time, direction)
        await bot.send_message(message.from_user.id, msg)
    log(command_autobet.__name__, message.from_user.id, msg)
    pass


#  LOGIN COMMANDS


@dp.message_handler(commands=['login'])
async def set_login(message):
    msg = str(message.text).replace('/login', '').replace(' ', '')
    if msg:
        USERS[message.from_user.id].login = msg
    ans = "Login: {0}".format(msg) if msg else "Forgot login..."
    await bot.send_message(message.from_user.id, ans)
    log(set_login.__name__, message.from_user.id, ans)
    pass


@dp.message_handler(commands=['pass'])
async def set_password(message):
    msg = str(message.text).replace('/pass', '').replace(' ', '')
    USERS[message.from_user.id].password = msg
    if USERS[message.from_user.id].login and USERS[message.from_user.id].password:
        USERS[message.from_user.id].dump()
    ans = "Password: {0}".format(msg) if msg else "Forgot pass..."
    await bot.send_message(message.from_user.id, ans)
    log(set_password.__name__, message.from_user.id, ans)
    pass


# CONNECT COMMANDS

@dp.message_handler(commands=['connect'])
async def command_connect(message):
    bm = Binarium()
    ans = "Connected successfully!"
    if not USERS[message.from_user.id].webdriver:
        try:
            bm.connect(USERS[message.from_user.id])
        except Exception as e:
            ans = e
    else:
        ans = "Already connected"
    await bot.send_message(message.from_user.id, ans)
    log(command_connect.__name__, message.from_user.id, ans)
    pass


@dp.message_handler(commands=['disconnect'])
async def command_disconnect(message):
    bm = Binarium()
    bm.disconnect(message.from_user.id)
    ans = "Disconnected successfully!"
    await bot.send_message(message.from_user.id, ans)
    log(command_disconnect.__name__, message.from_user.id, ans)
    pass


@dp.message_handler(lambda message: not USERS[message.from_user.id].webdriver)
async def any_message_from_disconnected_user(message):
    ans = "User not connected. Transferring to info function..."
    log(command_get_login_info.__name__, message.from_user.id, ans)
    await command_get_login_info(message)
    pass


@dp.message_handler(commands=['set_option'])
async def set_option(message):
    bm = Binarium()
    msg = str(message.text).replace('/setoption ', '')
    bm.set_option(USERS[message.from_user.id].webdriver, msg)
    ans = "Set Option: {0}".format(msg if msg else 'Demo')
    await bot.send_message(message.from_user.id, ans)
    log(set_option.__name__, message.from_user.id, ans)
    pass


@dp.message_handler(commands=['close_banners'])
async def close_banners(message):
    bm = Binarium()
    bm.close_banners(USERS[message.from_user.id].webdriver)
    await bot.send_message(message.from_user.id, "Banners closed!")
    pass


#

@dp.message_handler(commands=['wallet'])
async def set_wallet(message):
    bm = Binarium()
    msg = str(message.text).replace('/wallet', '').replace(' ', '').lower()
    real_wallet = msg.find('real') != -1
    bm.change_wallet(USERS[message.from_user.id].webdriver, real_wallet)
    ans = "Set Wallet: {0}".format(msg)
    await bot.send_message(message.from_user.id, ans)
    log(set_wallet.__name__, message.from_user.id, ans)
    pass


#
@dp.message_handler(commands=['time'])
async def set_time(message):
    bm = Binarium()
    msg = str(message.text).replace('/time', '').replace(' ', '')
    bm.set_time(USERS[message.from_user.id].webdriver, msg)
    ans = "Set Time: {0}".format(msg)
    await bot.send_message(message.from_user.id, ans)
    log(set_time.__name__, message.from_user.id, ans)
    pass


##
@dp.message_handler(commands=['sum'])
async def set_sum(message):
    bm = Binarium()
    msg = str(message.text).replace('/sum', '').replace(' ', '')
    bm.set_bet_sum(USERS[message.from_user.id].webdriver, msg)
    ans = "Set Sum: {0}".format(msg)
    await bot.send_message(message.from_user.id, ans)
    log(set_sum.__name__, message.from_user.id, ans)
    pass


##
@dp.message_handler(commands=['bet'])
async def do_bet(message):
    bm = Binarium()
    msg = str(message.text).replace('/bet', '').replace(' ', '')
    bm.bet(USERS[message.from_user.id].webdriver, msg)
    ans = "Bet {0}".format(msg)
    await bot.send_message(message.from_user.id, ans)
    log(do_bet.__name__, message.from_user.id, ans)
    pass


@dp.message_handler(commands=['active_bets'])
async def get_active_bets(message):
    bm = Binarium()
    if not USERS[message.from_user.id].webdriver:
        bm.connect(USERS[message.from_user.id])
    msg = prepare_bets_message(bm.get_active_bets(USERS[message.from_user.id].webdriver))
    await bot.send_message(message.from_user.id, msg)
    log(get_active_bets.__name__, message.from_user.id, "Got Active Bets")
    pass


@dp.message_handler(commands=['get_binarium_info'])
async def command_get_binarium_info(message):
    bm = Binarium()
    msg = prepare_info_message(bm.collect_info(USERS[message.from_user.id].webdriver))
    await bot.send_message(message.from_user.id, msg)
    log(command_get_binarium_info.__name__, message.from_user.id, "Got Binarium Account Info")
    pass


if __name__ == '__main__':
    asyncio.get_event_loop().create_task(autobet_inspector(bot))
    executor.start_polling(dp, skip_updates=True)
