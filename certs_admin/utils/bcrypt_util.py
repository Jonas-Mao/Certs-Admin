# -*- coding: utf-8 -*-

import bcrypt


def encode_password(password):
    """
    加密过程
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()

def check_password(password, hashed_password):
    """
    校验过程
    """
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

if __name__ == '__main__':
    print(encode_password('123456'))
    print(check_password('123456', '$2b$12$c/tJvOYaWxzis4CXSyGN9ua4B7wzor8j9WrGsgV/2pdJnsrAMJxiK'))
