# -*- coding: utf-8 -*-

from files.icp_util.icp_api import uomg_icp_api


def get_icp(domain):
    """
    备案查询网站：
    https://www.beianx.cn/
    https://beian.miit.gov.cn/#/Integrated/index
    :param domain:
    :return: ICPItem
    """
    # 第三方接口
    return uomg_icp_api.get_icp_from_uomg(domain)
