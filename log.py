import datetime

#
def log(func_name, status="OK", description=""):
    curr_time = datetime.datetime.now() - datetime.timedelta(microseconds=datetime.datetime.now().microsecond)
    curr_time = '{:^20}'.format(datetime.datetime.strftime(curr_time, '%Y-%m-%d %H:%M:%S'))
    func_name = '{:^30}'.format(func_name)
    status = '{:^30}'.format(status)
#    description = '{:^20}'.format(description)
    print(curr_time, '|', func_name, '|', status, '|', description)
