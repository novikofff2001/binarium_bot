from config import URL, WEBDRIVER_PATH, ALL_OPTIONS_PATH, ALL_TIMES_PATH, ALL_BANNERS_PATH
from log import log
from user import USER_INFO_TEMPLATE, ACTIVE_BET_TEMPLATE
#
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import time

BROWSER_TIMEOUT = 6  # seconds
WAIT_TIMEOUT = 3  # seconds
ALL_OPTIONS = [elem.replace('\n', '') for elem in open(ALL_OPTIONS_PATH, 'r')]
ALL_TIMES = [elem.replace('\n', '') for elem in open(ALL_TIMES_PATH, 'r')]


class Binarium:
    BANNERS_PATH = [elem.replace('\n', '') for elem in open(ALL_BANNERS_PATH, 'r')]

    def wait(self, driver, search_method, name, timeout=WAIT_TIMEOUT):
        try:
            element_present = EC.presence_of_element_located((search_method, name))
            WebDriverWait(driver, timeout).until(element_present)
            return 1
        except TimeoutException:
            return 0

    def connect(self, login, password):
        driver = webdriver.Chrome(WEBDRIVER_PATH)
        driver.get(URL)

        MAIN_WINDOW_PATH = 'cmp-nav-logo'
        if not self.wait(driver, By.CLASS_NAME, MAIN_WINDOW_PATH, BROWSER_TIMEOUT):
            raise Exception("Error! Page not loaded!")

        # Go to login form
        LOGIN_FORM_PATH = "//button[text()='Войти']"
        if not self.wait(driver, By.XPATH, LOGIN_FORM_PATH, BROWSER_TIMEOUT):
            raise Exception("Error! Login button not found!")
        driver.find_element_by_xpath(LOGIN_FORM_PATH).click()

        # login input
        LOGIN_FIELD_PATH = "//input[@formcontrolname='email']"
        if not self.wait(driver, By.XPATH, LOGIN_FIELD_PATH, BROWSER_TIMEOUT):
            raise Exception("Error! Login field not found!")
        driver.find_element_by_xpath(LOGIN_FIELD_PATH).send_keys(login)

        # password input
        PASSWORD_FIELD_PATH = "//input[@formcontrolname='password']"
        if not self.wait(driver, By.XPATH, PASSWORD_FIELD_PATH, BROWSER_TIMEOUT):
            raise Exception("Error! Password field not found!")
        driver.find_element_by_xpath(PASSWORD_FIELD_PATH).send_keys(password)

        # Enter click
        ENTER_BUTTON_PATH = "//button[@class='c-button ng-star-inserted']"
        if not self.wait(driver, By.XPATH, ENTER_BUTTON_PATH, BROWSER_TIMEOUT):
            raise Exception("Error! Enter button not found!")
        driver.find_element_by_xpath(ENTER_BUTTON_PATH).click()

        return driver

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
        #                webdriver.find_element_by_class_name(CHART_TAB_PATH).click()
        return 0

    def change_wallet(self, driver, real_wallet=False):
        try:
            CURRENT_WALLET = "//div[text()='{0}']".format("Реальный" if real_wallet else "Демосчет")
            driver.find_element_by_xpath(CURRENT_WALLET)
            return 1
        except NoSuchElementException:
            None
        #
        WALLET_BAR_PATH = "//div[@a-test='fullBalance']"
        WALLET_PATH = "//div[@a-test='{0}BalanceSum']".format("real" if real_wallet else "demo")
        for _ in range(2):
            try:
                if self.wait(driver, By.XPATH, WALLET_BAR_PATH):
                    driver.find_element_by_xpath(WALLET_BAR_PATH).click()
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

    def bet(self, driver, up):
        DOWN_BUTTON_PATH = "//div[@atest='buttonPut']"
        UP_BUTTON_PATH = "//div[@atest='buttonCall']"
        driver.find_element_by_xpath(UP_BUTTON_PATH if up else DOWN_BUTTON_PATH).click()
        pass

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
            result["profit_perсents"] = driver.find_element_by_class_name(PROFIT_PERSENTS_PATH).text

        PROFIT_SUM_PATH = "chart-profit__small"
        if self.wait(driver, By.CLASS_NAME, PROFIT_SUM_PATH):
            result["profit_sum"] = driver.find_element_by_class_name(PROFIT_SUM_PATH).text

        EXP_TIME_PATH = "//span[@a-test='currentExpiration']"
        if self.wait(driver, By.XPATH, EXP_TIME_PATH):
            result["time"] = driver.find_element_by_xpath(EXP_TIME_PATH).text
        print(result)
        return result

    def get_active_bets(self, driver):
        bet_num = int(1)
        result = {}
        HISTORY_BUTTON_PATH = "mm-button"
        if not self.wait(driver, By.CLASS_NAME, HISTORY_BUTTON_PATH):
            return result
        driver.find_element_by_class_name(HISTORY_BUTTON_PATH).click()
        if self.wait(driver, By.CLASS_NAME, "open-options-list"):
            for bet in driver.find_elements_by_class_name("open-option"):
                result[bet_num] = ACTIVE_BET_TEMPLATE.copy()
                result[bet_num]['time'] = bet.find_element_by_class_name("timer__text").text
                result[bet_num]["profit_sum"] = bet.find_element_by_class_name("open-option__income").text
                result[bet_num]["profit_perсents"] = bet.find_element_by_class_name("open-option__type").text
                result[bet_num]["bet_sum"] = bet.find_element_by_class_name("open-option__bet").text
                result[bet_num]["option"] = bet.find_element_by_class_name("open-option__asset").text
                bet_num += 1
        driver.find_element_by_class_name(HISTORY_BUTTON_PATH).click()
        print(result)
        return result
