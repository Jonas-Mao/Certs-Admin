# -*- coding: utf-8 -*-

import os
import base64


try:
    import secrets
except ImportError:
    secrets = None


# ******
def get_random_secret():
    """
    获取随机secret
    """
    if secrets:
        return secrets.token_hex()
    else:
        # 生成32位随机字符 编码为base64
        return base64.b64encode(os.urandom(32)).decode()


# *****
def get_random_password(size=6):
    """
    生成随机密码
    """
    return get_random_secret()[0:size]

if __name__ == '__main__':
    print(type(get_random_secret()))
    # print(get_random_password(6))
