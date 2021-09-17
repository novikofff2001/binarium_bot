from config import URL, WEBDRIVER_PATH, ALL_OPTIONS_PATH, ALL_TIMES_PATH
from log import log
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
WAIT_TIMEOUT = 3 # seconds
ALL_OPTIONS = [elem.replace('\n', '') for elem in open(ALL_OPTIONS_PATH, 'r')]
ALL_TIMES = [elem.replace('\n', '') for elem in open(ALL_TIMES_PATH, 'r')]


class Binarium:
    BANNERS_PATH = ["//div[@a-test='largestProfitabilityClose']",
                    "lt-wrapper-close",
                    "c-cookie-content",
                    ]

    def wait(self, webdriver, search_method, name, timeout=WAIT_TIMEOUT):
        try:
            element_present = EC.presence_of_element_located((search_method, name))
            WebDriverWait(webdriver, timeout).until(element_present)
            return 1
        except TimeoutException:
            return 0

    def connect(self, login, password):
        driver = webdriver.Chrome(WEBDRIVER_PATH)
        driver.get(URL)

        MAIN_WINDOW_PATH = 'cmp-nav-logo'
        present = self.wait(driver, By.CLASS_NAME, MAIN_WINDOW_PATH, BROWSER_TIMEOUT)
        if not present:
            raise Exception("Error! Page not loaded!")
        time.sleep(2)
        # Go to login form
        LOGIN_FORM_PATH = "//button[text()='Войти']"
        present = self.wait(driver, By.XPATH, LOGIN_FORM_PATH, BROWSER_TIMEOUT)
        if not present:
            raise Exception("Error! Login button not found!")
        driver.find_element_by_xpath(LOGIN_FORM_PATH).click()

        # login input
        LOGIN_FIELD_PATH = "//input[@formcontrolname='email']"
        present = self.wait(driver, By.XPATH, LOGIN_FIELD_PATH, BROWSER_TIMEOUT)
        if not present:
            raise Exception("Error! Login field not found!")
        driver.find_element_by_xpath(LOGIN_FIELD_PATH).send_keys(login)
        time.sleep(2)
        # password input
        PASSWORD_FIELD_PATH = "//input[@formcontrolname='password']"
        present = self.wait(driver, By.XPATH, PASSWORD_FIELD_PATH, BROWSER_TIMEOUT)
        if not present:
            raise Exception("Error! Password field not found!")
        driver.find_element_by_xpath(PASSWORD_FIELD_PATH).send_keys(password)
        time.sleep(2)
        # Enter click
        ENTER_BUTTON_PATH = "//button[@class='c-button ng-star-inserted']"
        present = self.wait(driver, By.XPATH, ENTER_BUTTON_PATH, BROWSER_TIMEOUT)
        if not present:
            raise Exception("Error! Enter button not found!")
        driver.find_element_by_xpath(ENTER_BUTTON_PATH).click()

        return driver

    def close_banners(self, webdriver):
        for elem in self.BANNERS_PATH:
            try:
                webdriver.find_element_by_xpath(elem).click()
            except:
                try:
                    webdriver.find_element_by_class_name(elem).click()
                except:
                    None
        log(self.close_banners.__name__, "OK", "All banners closed!")

    def set_option(self, webdriver, option, turbo=False):
        CURRENT_OPTION_PATH = 'chart-tab__asset'
        if self.wait(webdriver, By.CLASS_NAME, CURRENT_OPTION_PATH):
            CURRENT_OPTION_NAME = str(webdriver.find_element_by_class_name(CURRENT_OPTION_PATH).text)
            if option == CURRENT_OPTION_NAME:
                return 1
        CHART_TAB_PATH = 'chart-tab__toggle'
        BUTTON = "//div[@a-test='asset-{0}-{1}']".format('turbo' if turbo else 'binary', option)
        for _ in range(2):
            try:
                if self.wait(webdriver, By.CLASS_NAME, CHART_TAB_PATH):
                    webdriver.find_element_by_class_name(CHART_TAB_PATH).click()
                if self.wait(webdriver, By.XPATH, BUTTON):
                    webdriver.find_element_by_xpath(BUTTON).click()
                    return 1
            except ElementClickInterceptedException:
                self.close_banners(webdriver)
#                webdriver.find_element_by_class_name(CHART_TAB_PATH).click()
        return 0

    def change_wallet(self, webdriver, real_wallet=False):
        try:
            CURRENT_WALLET = "//div[text()='{0}']".format("Реальный" if real_wallet else "Демосчет")
            webdriver.find_element_by_xpath(CURRENT_WALLET)
            return 1
        except NoSuchElementException:
            None
        #
        WALLET_BAR_PATH = "//div[@a-test='fullBalance']"
        WALLET_PATH = "//div[@a-test='{0}BalanceSum']".format("real" if real_wallet else "demo")
        for _ in range(2):
            try:
                if self.wait(webdriver, By.XPATH, WALLET_BAR_PATH):
                    webdriver.find_element_by_xpath(WALLET_BAR_PATH).click()
                webdriver.find_element_by_xpath(WALLET_PATH).click()
                return 1
            except ElementClickInterceptedException:
                self.close_banners(webdriver)
        return 0

    def set_time(self, webdriver, time):
        CURRENT_EXPIRATION_PATH = "//span[@a-test='currentExpiration']"
        if self.wait(webdriver, By.XPATH, CURRENT_EXPIRATION_PATH):
            CURRENT_EXPIRATION = str(webdriver.find_element_by_xpath(CURRENT_EXPIRATION_PATH).text)
            if time == CURRENT_EXPIRATION:
                return 1
        NEW_TIME = "//div[text()='{0}']".format(time)
        for _ in range(2):
            if self.wait(webdriver, By.XPATH, CURRENT_EXPIRATION_PATH):
                try:
                    webdriver.find_element_by_xpath(CURRENT_EXPIRATION_PATH).click()
                    if self.wait(webdriver, By.XPATH, NEW_TIME):
                        webdriver.find_element_by_xpath(NEW_TIME).click()
                        return 1
                except ElementClickInterceptedException:
                    self.close_banners(webdriver)
#                   webdriver.find_element_by_xpath(CURRENT_EXPIRATION_PATH).click()
        return 0

    def set_bet_sum(self, webdriver, sum):
        SUM_FIELD_PATH = "//textarea[@a-test='chartBetValue']"
        if self.wait(webdriver, By.XPATH, SUM_FIELD_PATH):
            SUM_FIELD = str(webdriver.find_element_by_xpath(SUM_FIELD_PATH).text)
            if SUM_FIELD == sum:
                return 1
        #
        for _ in range(2):
            try:
                if self.wait(webdriver, By.XPATH, SUM_FIELD_PATH):
                    SUM_FIELD = webdriver.find_element_by_xpath(SUM_FIELD_PATH)
                    SUM_FIELD.click()
                    SUM_FIELD.send_keys(Keys.CONTROL + "a")
                    SUM_FIELD.send_keys(Keys.BACK_SPACE)
                    SUM_FIELD.send_keys(sum)
                    SUM_FIELD.send_keys(Keys.ENTER)
                    return 1
            except ElementClickInterceptedException:
                self.close_banners(webdriver)
        return 0