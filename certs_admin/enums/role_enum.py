# -*- coding: utf-8 -*-


class RoleEnum(object):
    """
    用户角色枚举值
    """
    # user
    USER = 0

    # admin
    ADMIN = 1

# 角色和权限对应关系
ROLE_PERMISSION = [
    {
        'role': RoleEnum.ADMIN,
        'permission': [RoleEnum.USER, RoleEnum.ADMIN]
    },
    {
        'role': RoleEnum.USER,
        'permission': [RoleEnum.USER]
    }
]
