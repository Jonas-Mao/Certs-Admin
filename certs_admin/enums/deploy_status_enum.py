# -*- coding: utf-8 -*-


class DeployStatusEnum(object):
    """
    部署状态枚举值
    """
    # 等待部署  默认
    PENDING = 0

    # 部署成功
    SUCCESS = 1

    # 部署失败
    ERROR = 2
