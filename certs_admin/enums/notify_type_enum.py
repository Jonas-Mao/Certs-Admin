# -*- coding: utf-8 -*-


class NotifyTypeEnum(object):
    """
    通知方式枚举值
    """
    # 未知
    Unknown = 0

    # 邮件
    Email = 1

    # 企业微信
    WORK_WEIXIN = 2

    # 钉钉
    DING_TALK = 3

    # webHook
    WebHook = 4

    # 飞书
    FEISHU = 5

    # 电报
    Telegram = 6
