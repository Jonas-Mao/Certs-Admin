# -*- coding: utf-8 -*-

from system.models import System


# ******
def get_system_config():
    """
    获取系统配置
    """
    rows = System.objects.all().values_list('key', 'value')

    config = {}
    for row in rows:
        config[row[0]] = row[1]

    return config


# ******
def get_config(key):
    return get_system_config().get(key)


'''
from certs_admin.config.env_config import PROMETHEUS_KEY
from certs_admin.enums.config_key_enum import ConfigKeyEnum
from certs_admin.utils.django_ext.app_exception import AppException


def check_email_config(config):
    if not config['mail_host']:
        raise AppException('未设置发件邮箱服务器地址')

    if not config['mail_port']:
        raise AppException('未设置发件邮箱服务器端口')

    if not config['mail_username']:
        raise AppException('未设置发件人邮箱账号')

    if not config['mail_password']:
        raise AppException('未设置发件人邮箱密码')


def get_email_config():
    config = get_system_config()

    return config


def init_system_config(app):
    """
    初始化全局常量配置
    :param app:
    """

    config = get_system_config()

    # 旧版本已存在
    app.config[ConfigKeyEnum.SECRET_KEY] = config[ConfigKeyEnum.SECRET_KEY]
    app.config[ConfigKeyEnum.TOKEN_EXPIRE_DAYS] = config[ConfigKeyEnum.TOKEN_EXPIRE_DAYS]

    # 兼容老版本 prometheus key
    if ConfigKeyEnum.PROMETHEUS_KEY in config:
        app.config[ConfigKeyEnum.PROMETHEUS_KEY] = config[ConfigKeyEnum.PROMETHEUS_KEY]
    else:
        System.objects.create(
            key=ConfigKeyEnum.PROMETHEUS_KEY,
            value=PROMETHEUS_KEY,
            label='prometheus_key',
            placeholder='prometheus_key'
        )
        app.config[ConfigKeyEnum.PROMETHEUS_KEY] = PROMETHEUS_KEY
'''
