import os.path
#
TOKEN_PATH = "token.txt"
TOKEN = str()
if os.path.exists(TOKEN_PATH):
    TOKEN = open(TOKEN_PATH, 'r').read()
else:
    open(TOKEN_PATH, 'w').close()
    raise Exception("Put bot's token in {0} file!".format(TOKEN_PATH))
#
ADMINISTRATORS_PATH = "admins.txt"
ADMINISTRATORS = set()
if os.path.exists(ADMINISTRATORS_PATH):
    for elem in open(ADMINISTRATORS_PATH, 'r').readlines():
        ADMINISTRATORS.add(int(elem))
else:
    open(ADMINISTRATORS_PATH, 'w').close()
if len(ADMINISTRATORS) == 0:
    print("WARN: There is no administrators at this bot")
#
USERS_PATH = 'users/'
ICONS_PATH = 'icons/'
WEBDRIVER_PATH = 'webdriver/chromedriver.exe'
ALL_OPTIONS_PATH = 'database/all_options.txt'
ALL_TIMES_PATH = 'database/all_times.txt'
ALL_BANNERS_PATH = 'database/all_banners.txt'
#
URL = 'https://binarium.global'
WELCOME_MESSAGE = """Welcome to Binarium bot! Set login and password using /login and /pass"""
