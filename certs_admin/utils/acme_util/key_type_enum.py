# -*- coding: utf-8 -*-

import OpenSSL


class KeyTypeEnum(object):
    """
    加密方式
    """
    RSA = "RSA"
    EC = "EC"
    DSA = "DSA"
    DH = "DH"

KEY_TYPE_OPTIONS = [
    {
        'label': "RSA",
        'value': KeyTypeEnum.RSA,
        'type': OpenSSL.crypto.TYPE_RSA
    },
    {
        'label': "EC",
        'value': KeyTypeEnum.EC,
        'type': OpenSSL.crypto.TYPE_EC
    },
    {
        'label': "DSA",
        'value': KeyTypeEnum.DSA,
        'type': OpenSSL.crypto.TYPE_DSA
    },
    {
        'label': "DH",
        'value': KeyTypeEnum.DH,
        'type': OpenSSL.crypto.TYPE_DH
    },
]

def get_key_type_option(value):
    for item in KEY_TYPE_OPTIONS:
        if item['value'] == value:
            return item

def get_key_type(value):
    item = get_key_type_option(value)
    if item:
        return item['type']
