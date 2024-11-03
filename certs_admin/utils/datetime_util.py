# -*- coding: utf-8 -*-

import sys
import time
from datetime import datetime


DATETIME_WITH_MICROSECOND_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

DATETIME_SHORT_FORMAT = "%Y-%m-%d %H:%M"

DATE_FORMAT = "%Y-%m-%d"

TIME_FORMAT = "%H:%M:%S"

class TimeEnum(object):
    Second = 1
    Minute = 60 * Second
    Hour = 60 * Minute
    Day = 24 * Hour

def get_timestamp(datetime_obj):
    return int(time.mktime(datetime_obj.timetuple()))

def get_timestamp_with_microsecond(datetime_obj):
    if sys.version_info[0] < 3 or sys.version_info[1] < 4:
        # python version < 3.3
        return int(time.mktime(datetime_obj.timetuple()) * 1000)
    else:
        return int(datetime_obj.timestamp() * 1000)

def get_datetime():
    return datetime.now().strftime(DATETIME_FORMAT)

def get_datetime_with_microsecond():
    return datetime.now().strftime(DATETIME_WITH_MICROSECOND_FORMAT)

def parse_datetime(datetime_str):
    return datetime.strptime(datetime_str, DATETIME_FORMAT)

def get_date():
    return datetime.now().strftime(DATE_FORMAT)

def format_datetime(date_time):
    return datetime.strftime(date_time, DATETIME_FORMAT)

def format_date(date_time):
    return datetime.strftime(date_time, DATE_FORMAT)

def format_time(date_time):
    return datetime.strftime(date_time, TIME_FORMAT)


def format_datetime_label(date_time):
    if not isinstance(date_time, datetime):
        return

    now = datetime.now()

    if now.day == date_time.day:
        return format_time(date_time)
    else:
        return format_date(date_time)


def microsecond_for_human(value):
    """
    将时间格式化为: 1d 2h 3m 4s 5ms
    """
    if value is None:
        return

    MICROSECOND = 1
    SECOND = MICROSECOND * 1000
    MINUTE = SECOND * 60
    HOUR = MINUTE * 60
    DAY = HOUR * 24

    lst = []

    if value >= DAY:
        days, value = divmod(value, DAY)
        lst.append(str(days) + 'd')

    if value >= HOUR:
        hours, value = divmod(value, HOUR)
        lst.append(str(hours) + 'h')

    if value >= MINUTE:
        minutes, value = divmod(value, MINUTE)
        lst.append(str(minutes) + 'm')

    if value >= SECOND:
        seconds, value = divmod(value, SECOND)
        lst.append(str(seconds) + 's')

    if value > 0:
        lst.append(str(value) + 'ms')

    if len(lst) == 0:
        lst.append('0ms')

    return ' '.join(lst)


def seconds_for_human(seconds):
    """
    将时间格式化为: 1d 2h 3m 4s
    :param seconds:
    :return:
    """
    return microsecond_for_human(seconds * 1000)


def get_diff_time(start_date, end_date):
    """
    获取两个时间对象的时间差秒数
    """
    if start_date and end_date \
            and isinstance(start_date, datetime) \
            and isinstance(end_date, datetime):
        return get_timestamp(end_date) - get_timestamp(start_date)
    else:
        return 0    # False


def get_diff_time_with_microsecond(start_date, end_date):
    """
    获取两个时间对象的时间差秒数
    """
    if start_date and end_date \
            and isinstance(start_date, datetime) \
            and isinstance(end_date, datetime):
        return get_timestamp_with_microsecond(end_date) - get_timestamp_with_microsecond(start_date)
    else:
        return 0


def is_less_than(source_date, target_date):
    # source_date - target_date < 0
    return get_diff_time(target_date, source_date) < 0


#
def is_greater_than(source_date, target_date):
    # source_date - target_date > 0
    return get_diff_time(target_date, source_date) > 0
