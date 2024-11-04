# -*- coding: utf-8 -*-

import os
from cryptography.fernet import Fernet

crypto_key = os.path.join('/certs_admin/config', 'crypto.key')


def encrypt_password(password):
    key = Fernet.generate_key()
    cipher = Fernet(key)
    key = key.decode()

    with open('crypto.key', 'w') as f:
        f.write(f"{key}\t")

    return cipher.encrypt(password.encode()).decode()


def decrypt_password():
    with open(crypto_key, 'r') as f:
        content = f.read()
        key, en_pass = content.split('\t')

    cipher = Fernet(key)
    return cipher.decrypt(en_pass)
