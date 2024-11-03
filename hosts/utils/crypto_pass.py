# -*- coding: utf-8 -*-

import os
import shutil
from cryptography.fernet import Fernet
from datetime import datetime

crypto_host = os.path.join('/Users/Jonas.Mao/Desktop/certs_admin/hosts/utils', 'crypto.key')


def encrypt_pass(password, host):
    """
    加密
    """
    key = Fernet.generate_key()
    cipher = Fernet(key)
    key = key.decode()

    unique_host(crypto_host, host, key)

    return cipher.encrypt(password.encode()).decode()


def unique_host(file, host, key):
    """
    去重
    """
    now = datetime.now().strftime('%Y%m%d%H%M%S')
    date = datetime.now().strftime('%Y%m%d')
    file_tmp = f"{file}-{date}"

    if os.path.exists(file_tmp):
        os.remove(file_tmp)
    shutil.copy(file, file_tmp)

    with open(file_tmp, 'r') as f1:
        lines = f1.readlines()

    with open(file, 'w') as f2:
        for line in lines:
            if host != line.split(':', 1)[0]:
                f2.write(line)
        f2.write(f"{host}:{key}:{now}\n")


def decrypt_pass(en_password, host_ip):
    """
    解密
    """
    with open(crypto_host, 'r') as f:
        for line in f:
            host, key, date = line.split(':')
            if host_ip == host:
                cipher = Fernet(key)
                return cipher.decrypt(en_password.encode('utf-8')).decode('utf-8')