# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil import parser
from dateutil.tz import tzlocal

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'   # 时间格式化


# ******
def parse_time(time_str):
    """
    解析字符串为时间
    """
    return datetime.strptime(
        parser.parse(time_str).astimezone(tzlocal()).strftime(DATETIME_FORMAT),
        DATETIME_FORMAT
    )


# ******
def get_diff_days(start_date, end_date):
    """
    获取两个时间对象的时间差天数
    :param start_date: [datetime, DateTimeField]
    :param end_date: [datetime, DateTimeField]
    """
    if start_date and end_date \
            and isinstance(start_date, datetime) \
            and isinstance(end_date, datetime):
        return (end_date - start_date).days
    else:
        return 0
