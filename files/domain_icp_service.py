# -*- coding: utf-8 -*-

from datetime import datetime
from certs_admin.utils import datetime_util
from files.icp_util.icp_main import get_icp
from files.icp_util.icp_item import ICPItem
from domain_ipaddr.models import DomainInfo


def get_domain_icp(domain):
    """
    获取域名icp数据
    """
    domain_icp_row = DomainInfo.objects.get(domain=domain)

    is_expired = datetime_util.is_less_than(domain_icp_row.expire_time, datetime.now())

    if domain_icp_row and not is_expired:
        item = ICPItem()
        item.domain = domain
        item.icp = domain_icp_row.icp_licence
        item.name = domain_icp_row.icp_company
    else:
        item = None

        try:
            item = get_icp(domain)
        except Exception as e:
            print('获取域名ICP数据失败%s' %e)

    return item
