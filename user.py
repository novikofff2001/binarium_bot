import datetime
import os.path
import pickle
#
from config import USERS_PATH, ADMINISTRATORS
from selenium.common.exceptions import WebDriverException
from log import log

#

USERS = {}

USER_INFO_TEMPLATE = {
    "money": None,
    "real_wallet": None,
    "bet_sum": None,
    "option": None,
    "profit_percents": None,
    "profit_sum": None,
    "time": None,
}


class Whitelist:
    wl = set(ADMINISTRATORS.copy())
    FILENAME = 'whitelist.txt'

    #
    def __init__(self):
        self.load()

    def load(self):
        with open(USERS_PATH + self.FILENAME, 'r') as f:
            self.wl.update([int(user_id) for user_id in f.readlines()])

    def dump(self):
        with open(USERS_PATH + self.FILENAME, 'w') as f:
            for elem in self.wl:
                if elem not in ADMINISTRATORS:
                    f.write('{0}\n'.format(elem))


class User:
    # base info
    id = None
    login = None
    password = None

    autobet = {'sum': '60.0', 'real_wallet': False}

    # additional info
    webdriver = None
    last_activity = datetime.datetime(1970, 1, 1, 0, 0, 0)

    def __init__(self, user_id):
        self.id = user_id
        if os.path.isfile(USERS_PATH + '%d.pkl' % user_id):
            self.load(user_id)

    def dump(self):
        with open(USERS_PATH + '%d.pkl' % self.id, 'wb') as f:
            driver = self.webdriver
            self.webdriver = None
            pickle.dump(self, f)
            self.webdriver = driver
            log('USER_DUMP', self.id, 'Dumped successfully!')

    def load(self, user_id):
        with open(USERS_PATH + '%d.pkl' % user_id, 'rb') as f:
            data = pickle.load(f)
            self.login = data.login
            self.password = data.password
            self.autobet = data.autobet
        log('USER_LOAD', self.id, 'Loaded successfully!')

    def alive(self):
        try:
            log("ALIVE_CHECK", self.id, "Browser Alive: {}".format(self.webdriver.session_id))
            return 1
        except (WebDriverException, AttributeError) as e:
            log("ALIVE_CHECK", self.id, "Browser Dead: {}".format(e))
            return 0
