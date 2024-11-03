# -*- coding: utf-8 -*-

from datetime import date, timedelta

# 资源创建时间格式化
def timestamp_format(timestamp):
    c = timestamp + timedelta(hours=8)
    t = date.strftime(c, '%Y-%m-%d %H:%M:%S')
    return t
