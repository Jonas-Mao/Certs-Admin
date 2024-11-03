# -*- coding: utf-8 -*-


def byte_to_str(dict):
    """
    转换字典value值为字符串，默认生成的pkey_pem为b''字节类型
    """
    for k, v in dict.items():
        if isinstance(v, bytes):
            dict[k] = str(v, encoding='utf-8')

    return dict
