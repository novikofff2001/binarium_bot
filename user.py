import datetime
import os.path
import pickle
#
from config import USERS_PATH, ADMINISTRATORS
from log import log

#

USERS = {}


class Whitelist:
    wl = set(ADMINISTRATORS.copy())
    FILENAME = 'whitelist.txt'

    #
    def __init__(self):
        self.load()
        pass

    def load(self):
        self.wl.clear()
        with open(USERS_PATH + self.FILENAME, 'r') as f:
            self.wl.append(f.readline())

    def dump(self):
        with open(USERS_PATH + self.FILENAME, 'w') as f:
            for elem in self.wl:
                f.write(elem)


class User:
    # base info
    id = None
    login = None
    password = None
    autobet_params = {'sum': None, 'real_wallet': False}

    # additional info
    webdriver = None
    connected = False
    last_activity = datetime.datetime(1970, 1, 1, 0, 0, 0)

    def __init__(self, user_id):
        self.id = user_id
        if os.path.isfile(USERS_PATH + '%d.pkl' % user_id):
            self.load(user_id)

    def get_base_info(self):
        return {self.id, self.login, self.password, self.autobet_params}

    def dump(self):
        with open(USERS_PATH + '%d.pkl' % self.id, 'wb') as f:
            pickle.dump(self, f)
            log('USER_DUMP', self.id, 'Dumped successfully!')

    def load(self, user_id):
        with open(USERS_PATH + '%d.pkl' % user_id, 'rb') as f:
            data = pickle.load(f)
            self.login = data.login
            self.password = data.password
            self.autobet_params = data.autobet_params
        log('USER_LOAD', self.id, 'Loaded successfully!')


for user_id in Whitelist.wl:
    USERS[user_id] = User(user_id)
