import datetime
import pytz

from config import TIMEZONE


#
def log(func_name, status="OK", description=""):
    curr_time = datetime.datetime.now(pytz.timezone(TIMEZONE))
    curr_time = '{:^20}'.format(datetime.datetime.strftime(curr_time, '%Y-%m-%d %H:%M:%S'))
    func_name = '{:^30}'.format(func_name)
    status = '{:^30}'.format(status)
    description = '{:^20}'.format(description.replace('\n', ' '))
    print(curr_time, '|', func_name, '|', status, '|', description)
