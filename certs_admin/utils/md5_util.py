# -*- coding: utf-8 -*-

import hashlib

def md5(msg):
    """
    获取字符串的md5值
    :param msg:
    :return: str
    """
    return hashlib.md5(msg.encode("utf-8")).hexdigest()
