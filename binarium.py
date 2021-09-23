import asyncio
import datetime
import codecs

from config import WEBDRIVER_PATH, ALL_OPTIONS_PATH, ALL_TIMES_PATH, ALL_BANNERS_PATH
from log import log
from user import USERS, USER_INFO_TEMPLATE
#
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver

URL = 'https://binarium.global'
BROWSER_TIMEOUT = 6  # seconds
WAIT_TIMEOUT = 3  # seconds

ACTIVE_BET_TEMPLATE = {
    "timer": None,
    "profit_sum": None,
    "profit_percents": None,
    "bet_sum": None,
    "option": None
}


AUTOBET_TEMPLATE = {'signal_time': None,
                   'option': None,
                   'exp_time': None,
                   'direction': None}

AUTOBET_QUEUE = {}


def prepare_info_message(result):
    msg = '=' * 30 + '\n'
    msg += "money:{0}\n".format(result['money'])
    msg += "real_wallet:{0}\n".format(result['real_wallet'])
    msg += "bet_sum:{0}\n".format(result['bet_sum'])
    msg += "profit_percents:{0}\n".format(result['profit_percents'])
    msg += "profit_sum:{0}\n".format(result['profit_sum'])
    msg += "time:{0}\n".format(result['time'])
    if len(msg) == 0:
        msg = 'No Info'
    return msg


def prepare_bets_message(result):
    msg = ''
    bet_num = int(0)
    for key in result.keys():
        bet_num += 1
        msg += '{:=^30}\n'.format("Active bet №{0}".format(bet_num))
        msg += 'Option: {0}\n'.format(result[key]['option'])
        msg += 'expiration time: {0}\n'.format(result[key]['timer'])
        msg += 'Sum of bet: {0}\n'.format(result[key]['bet_sum'])
        msg += 'Profit sum: {0}\n'.format(result[key]['profit_sum'])
        msg += 'Profit percents: {0}\n'.format(result[key]['profit_percents'])
    if len(msg) == 0:
        msg = 'No Active bets'
    return msg


class Binarium:
    BANNERS_PATH = []
    ALL_OPTIONS = []
    ALL_TIMES = []

    def __init__(self):
        self.BANNERS_PATH = [_.replace('\n', '') for _ in codecs.open(ALL_BANNERS_PATH, 'r', 'cp1251').readlines()]
        self.ALL_OPTIONS = [_.replace('\n', '') for _ in open(ALL_OPTIONS_PATH, 'r').readlines()]
        self.ALL_TIMES = [_.replace('\n', '') for _ in open(ALL_TIMES_PATH, 'r').readlines()]

    def wait(self, driver, search_method, name, timeout=WAIT_TIMEOUT):
        try:
            element_present = EC.presence_of_element_located((search_method, name))
            WebDriverWait(driver, timeout).until(element_present)
            return 1
        except TimeoutException:
            return 0

    def connect(self, user_id):
        assert USERS[user_id].login and USERS[user_id].password
        driver = webdriver.Chrome(WEBDRIVER_PATH)
        driver.get(URL)

        connected = 1
        MAIN_WINDOW_PATH = 'cmp-nav-logo'
        if not self.wait(driver, By.CLASS_NAME, MAIN_WINDOW_PATH, BROWSER_TIMEOUT):
            connected = 0

        # Go to login form
        LOGIN_FORM_PATH = "//button[text()='Войти']"
        if self.wait(driver, By.XPATH, LOGIN_FORM_PATH, BROWSER_TIMEOUT):
            driver.find_element_by_xpath(LOGIN_FORM_PATH).click()
        else:
            connected = 0

        # login input
        LOGIN_FIELD_PATH = "//input[@formcontrolname='email']"
        if self.wait(driver, By.XPATH, LOGIN_FIELD_PATH, BROWSER_TIMEOUT):
            driver.find_element_by_xpath(LOGIN_FIELD_PATH).send_keys(USERS[user_id].login)
        else:
            connected = 0

        # password input
        PASSWORD_FIELD_PATH = "//input[@formcontrolname='password']"
        if self.wait(driver, By.XPATH, PASSWORD_FIELD_PATH, BROWSER_TIMEOUT):
            driver.find_element_by_xpath(PASSWORD_FIELD_PATH).send_keys(USERS[user_id].password)
        else:
            connected = 0

        # Enter click
        ENTER_BUTTON_PATH = "//button[@class='c-button ng-star-inserted']"
        if self.wait(driver, By.XPATH, ENTER_BUTTON_PATH, BROWSER_TIMEOUT):
            driver.find_element_by_xpath(ENTER_BUTTON_PATH).click()
        else:
            connected = 0

        if connected:
            return driver
        else:
            driver.quit()
            return None

    def close_banners(self, driver):
        for elem in self.BANNERS_PATH:
            try:
                driver.find_element_by_xpath(elem).click()
            except:
                try:
                    driver.find_element_by_class_name(elem).click()
                except:
                    None
        log(self.close_banners.__name__, "OK", "All banners closed!")

    def set_option(self, driver, option, turbo=False):
        CURRENT_OPTION_PATH = 'chart-tab__asset'
        if self.wait(driver, By.CLASS_NAME, CURRENT_OPTION_PATH):
            CURRENT_OPTION_NAME = str(driver.find_element_by_class_name(CURRENT_OPTION_PATH).text)
            if option == CURRENT_OPTION_NAME:
                return 1
        CHART_TAB_PATH = 'chart-tab__toggle'
        BUTTON = "//div[@a-test='asset-{0}-{1}']".format('turbo' if turbo else 'binary', option)
        for _ in range(2):
            try:
                if self.wait(driver, By.CLASS_NAME, CHART_TAB_PATH):
                    driver.find_element_by_class_name(CHART_TAB_PATH).click()
                if self.wait(driver, By.XPATH, BUTTON):
                    driver.find_element_by_xpath(BUTTON).click()
                    return 1
            except ElementClickInterceptedException:
                self.close_banners(driver)
        return 0

    def change_wallet(self, driver, real_wallet=False):
        CURRENT_WALLET = "//div[text()='{0}']".format("Реальный" if real_wallet else "Демосчет")
        if self.wait(driver, By.XPATH, CURRENT_WALLET):
            return 1
        #
        WALLET_BAR_PATH = "//div[@a-test='fullBalance']"
        WALLET_PATH = "//div[@a-test='{0}BalanceSum']".format("real" if real_wallet else "demo")
        for _ in range(2):
            try:
                if self.wait(driver, By.XPATH, WALLET_BAR_PATH):
                    driver.find_element_by_xpath(WALLET_BAR_PATH).click()
                if self.wait(driver, By.XPATH, WALLET_PATH):
                    driver.find_element_by_xpath(WALLET_PATH).click()
                return 1
            except ElementClickInterceptedException:
                self.close_banners(driver)
        return 0

    def set_time(self, driver, time):
        CURRENT_EXPIRATION_PATH = "//span[@a-test='currentExpiration']"
        if self.wait(driver, By.XPATH, CURRENT_EXPIRATION_PATH):
            CURRENT_EXPIRATION = str(driver.find_element_by_xpath(CURRENT_EXPIRATION_PATH).text)
            if time == CURRENT_EXPIRATION:
                return 1
        NEW_TIME = "//div[text()='{0}']".format(time)
        for _ in range(2):
            if self.wait(driver, By.XPATH, CURRENT_EXPIRATION_PATH):
                try:
                    driver.find_element_by_xpath(CURRENT_EXPIRATION_PATH).click()
                    if self.wait(driver, By.XPATH, NEW_TIME):
                        driver.find_element_by_xpath(NEW_TIME).click()
                        return 1
                except ElementClickInterceptedException:
                    self.close_banners(driver)
        #                   webdriver.find_element_by_xpath(CURRENT_EXPIRATION_PATH).click()
        return 0

    def set_bet_sum(self, driver, sum):
        SUM_FIELD_PATH = "//textarea[@a-test='chartBetValue']"
        if self.wait(driver, By.XPATH, SUM_FIELD_PATH):
            SUM_FIELD = str(driver.find_element_by_xpath(SUM_FIELD_PATH).text)
            if SUM_FIELD == sum:
                return 1
        #
        for _ in range(2):
            try:
                if self.wait(driver, By.XPATH, SUM_FIELD_PATH):
                    SUM_FIELD = driver.find_element_by_xpath(SUM_FIELD_PATH)
                    SUM_FIELD.click()
                    SUM_FIELD.send_keys(Keys.CONTROL + "a")
                    SUM_FIELD.send_keys(Keys.BACK_SPACE)
                    SUM_FIELD.send_keys(sum)
                    SUM_FIELD.send_keys(Keys.ENTER)
                    return 1
            except ElementClickInterceptedException:
                self.close_banners(driver)
        return 0

    def bet(self, driver, msg=str()):
        is_up = msg.lower().find('верх') != -1 and msg.lower().find('вниз') == -1
        DOWN_BUTTON_PATH = "//div[@atest='buttonPut']"
        UP_BUTTON_PATH = "//div[@atest='buttonCall']"
        for _ in range(2):
            try:
                driver.find_element_by_xpath(UP_BUTTON_PATH if is_up else DOWN_BUTTON_PATH).click()
                return 1
            except ElementClickInterceptedException:
                self.close_banners(driver)
        return 0

    def collect_info(self, driver):
        result = USER_INFO_TEMPLATE.copy()

        BALANCE_PATH = "//div[@a-test='fullBalance']"
        if self.wait(driver, By.XPATH, BALANCE_PATH):
            result['money'] = driver.find_element_by_xpath(BALANCE_PATH).text

        WALLET_TYPE_PATH = "wallet-menu-total__name"
        if self.wait(driver, By.CLASS_NAME, WALLET_TYPE_PATH):
            result['real_wallet'] = driver.find_element_by_class_name(WALLET_TYPE_PATH).text

        BET_SUM_PATH = "//textarea[@a-test='chartBetValue']"
        if self.wait(driver, By.XPATH, BET_SUM_PATH):
            result["bet_sum"] = driver.find_element_by_xpath(BET_SUM_PATH).get_attribute('value')

        CURRENCY_PATH = "chart-bet-control__currency"
        if self.wait(driver, By.CLASS_NAME, CURRENCY_PATH):
            result['bet_sum'] += ' ' + driver.find_element_by_class_name(CURRENCY_PATH).text

        OPTION_NAME_PATH = "chart-tab__asset"
        if self.wait(driver, By.CLASS_NAME, OPTION_NAME_PATH):
            result["option"] = driver.find_element_by_class_name(OPTION_NAME_PATH).text

        PROFIT_PERSENTS_PATH = "chart-profit__large"
        if self.wait(driver, By.CLASS_NAME, PROFIT_PERSENTS_PATH):
            result["profit_percents"] = driver.find_element_by_class_name(PROFIT_PERSENTS_PATH).text

        PROFIT_SUM_PATH = "chart-profit__small"
        if self.wait(driver, By.CLASS_NAME, PROFIT_SUM_PATH):
            result["profit_sum"] = driver.find_element_by_class_name(PROFIT_SUM_PATH).text

        EXP_TIME_PATH = "//span[@a-test='currentExpiration']"
        if self.wait(driver, By.XPATH, EXP_TIME_PATH):
            result["time"] = driver.find_element_by_xpath(EXP_TIME_PATH).text
        return result

    def get_active_bets(self, driver):
        bet_num = int(1)
        result = {}
        HISTORY_BUTTON_PATH = "mm-button"
        for _ in range(2):
            try:
                if self.wait(driver, By.CLASS_NAME, HISTORY_BUTTON_PATH):
                    driver.find_element_by_class_name(HISTORY_BUTTON_PATH).click()
                    break
                else:
                    return result
            except ElementClickInterceptedException:
                self.close_banners(driver)

        if self.wait(driver, By.CLASS_NAME, "open-options-list"):
            for bet in driver.find_elements_by_class_name("open-option"):
                result[bet_num] = ACTIVE_BET_TEMPLATE.copy()

                TIMER_PATH = "timer__text"
                if self.wait(driver, By.CLASS_NAME, TIMER_PATH):
                    result[bet_num]['timer'] = str(bet.find_element_by_class_name(TIMER_PATH).text).replace(':', '')

                PROFIT_VALUE_PATH = "open-option__income"
                if self.wait(driver, By.CLASS_NAME, PROFIT_VALUE_PATH):
                    result[bet_num]["profit_sum"] = bet.find_element_by_class_name(PROFIT_VALUE_PATH).text

                PROFIT_PERCENTS_PATH = "open-option__type"
                if self.wait(driver, By.CLASS_NAME, PROFIT_PERCENTS_PATH):
                    result[bet_num]["profit_percents"] = bet.find_element_by_class_name(PROFIT_PERCENTS_PATH).text

                BET_SUM_PATH = "open-option__bet"
                if self.wait(driver, By.CLASS_NAME, BET_SUM_PATH):
                    result[bet_num]["bet_sum"] = bet.find_element_by_class_name(BET_SUM_PATH).text

                OPTION_PATH = "open-option__asset"
                if self.wait(driver, By.CLASS_NAME, OPTION_PATH):
                    result[bet_num]["option"] = bet.find_element_by_class_name(OPTION_PATH).text

                bet_num += 1
        self.close_banners(driver)
        return result

    def add_autobet(self, user_id, option, exp_time, direction):
        autobet = AUTOBET_TEMPLATE.copy()
        autobet['signal_time'] = datetime.datetime.now()
        autobet['option'] = option
        autobet['exp_time'] = exp_time
        autobet['direction'] = direction
        if user_id not in AUTOBET_QUEUE:
            AUTOBET_QUEUE[user_id] = []
        AUTOBET_QUEUE[user_id].append(autobet)

    def is_option(self, elem):
        return elem.upper() in self.ALL_OPTIONS

    def is_time(self, elem):
        return elem in self.ALL_TIMES

    def is_direction(self, elem):
        return elem.lower().find('вниз') != -1 or elem.lower().find('верх') != -1


async def autobet_inspector(bot):
    while True:
        bm = Binarium()
        queue_copy = AUTOBET_QUEUE.copy()
        for user_id in queue_copy.keys():
            for autobet in queue_copy[user_id]:
                if not USERS[user_id].webdriver:
                    USERS[user_id].webdriver = bm.connect(user_id)
                #
                bm.change_wallet(USERS[user_id].webdriver, USERS[user_id].autobet['real_wallet'])
                success = bm.set_option(USERS[user_id].webdriver, autobet['option'])
                if success:
                    bm.set_time(USERS[user_id].webdriver, autobet['exp_time'])
                    bm.set_bet_sum(USERS[user_id].webdriver, USERS[user_id].autobet['sum'])
                    bm.bet(USERS[user_id].webdriver, autobet['direction'])
                await asyncio.sleep(2)
            AUTOBET_QUEUE[user_id] = [elem for elem in AUTOBET_QUEUE[user_id] if elem not in queue_copy[user_id]]
            await bot.send_message(user_id, prepare_bets_message(bm.get_active_bets(USERS[user_id].webdriver)))
            if len(AUTOBET_QUEUE[user_id]) == 0:
                AUTOBET_QUEUE.pop(user_id)
        await asyncio.sleep(2)
