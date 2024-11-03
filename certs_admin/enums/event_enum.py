# -*- coding: utf-8 -*-


class EventEnum(object):
    """
    通知事件枚举值
    """
    # SSL证书到期（默认）
    SSL_CERT_EXPIRE = 1

    # 托管证书到期
    SSL_CERT_FILE_EXPIRE = 2

    # 监控异常
    MONITOR_EXCEPTION = 3

    # 监控异常恢复
    MONITOR_EXCEPTION_RESTORE = 4
