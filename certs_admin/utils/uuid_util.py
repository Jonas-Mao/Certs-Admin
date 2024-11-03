# -*- coding: utf-8 -*-

import uuid


def get_uuid():
    """
    返回36位的uuid
    :return: eg: 2817cac5-d65f-4fec-8e78-1bdaf55655e8
    """
    return str(uuid.uuid4())


if __name__ == '__main__':
    print(get_uuid())
