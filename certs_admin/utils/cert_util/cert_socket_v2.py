# -*- coding: utf-8 -*-

"""
参考：python批量检查通一个集群针对同一个域名解析到不同IP地址证书的有效性
https://blog.csdn.net/reblue520/article/details/106832780
"""

import socket
import ssl
from certs_admin.utils import time_util
import logging
logger = logging.getLogger('certs-admin')


def get_domain_host_list(domain, port=80):
    """
    获取域名映射主机地址列表，一对多关系
    """
    res = socket.getaddrinfo(
        domain,
        port,
        socket.AF_INET,     # 限制仅返回IPv4
        0,
        socket.IPPROTO_TCP
    )

    lst = []
    for item in res:
        lst.append(item[4][0])

    return lst


def get_ssl_cert(domain, host=None, port=443, timeout=3):
    """
    获取主机证书信息
    :return: Dict
    """
    logger.info(
        {
            'domain': domain,
            'host': host,
            'port': port,
            'timeout': timeout
        })

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    sock.connect((host, port))

    ssl_context = ssl.create_default_context()

    wrap_socket = ssl_context.wrap_socket(sock, server_hostname=domain)
    cert = wrap_socket.getpeercert()
    wrap_socket.close()

    return cert


def get_ssl_cert_info(domain, host=None, port=443, timeout=3):
    """
    返回解析好的证书信息数据
    """
    cert = get_ssl_cert(domain, host, port, timeout)

    return resolve_cert(cert)


def resolve_cert(cert):
    """
    解析证书信息，仅解析重要信息
    :param cert: Dict
    """
    data = {
        "start_date": time_util.parse_time(cert['notBefore']),
        "expire_date": time_util.parse_time(cert['notAfter']),
    }

    return data


if __name__ == '__main__':
    print(get_domain_host_list('www.taobao.com'))
    # print(get_ssl_cert_info('www.taobao.com', '111.62.93.139'))
    # print(get_ssl_cert_info('38.60.47.102', '38.60.47.102'))
    # print('www.baidu.com'.encode('idna')) # b'www.baidu.com'
    # print('www.baidu.com'.encode('punycode')) # b'www.baidu.com-'
