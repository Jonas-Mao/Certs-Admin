# -*- coding: utf-8 -*-

from certs.utils.get_cert_info import expire_info, ips_count
from files.domain_util import get_root_domain


def certs_expire(domain, port=443):
    """
    证书时间
    """
    return expire_info(domain, port)


def cert_ips(domain):
    """
    主机数量
    """
    return ips_count(domain)


def certs_root_domain(domain):
    """
    根域名
    """
    try:
        root_domain = get_root_domain(domain)
    except:
        root_domain = None

    return root_domain


def certs_status(domain, port):
    """
    判断状态
    """
    ssl_expire = certs_expire(domain, port)

    if ssl_expire.get('remaining_days'):
        status = 'verified'
    else:
        status = 'unverified'

    return status
