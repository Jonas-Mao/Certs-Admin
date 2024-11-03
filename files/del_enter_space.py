# -*- coding: utf-8 -*-


def remove_in_special_chars(data):
    """
    删除键值里面的\n\t符号
    """
    if isinstance(data, dict):
        return {k: remove_in_special_chars(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [remove_in_special_chars(item) for item in data]
    elif isinstance(data, str):
        return data.replace('\n', '').replace('\t', '')
    else:
        return data