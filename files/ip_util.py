# -*- coding: utf-8 -*-

import socket
import requests


def get_ip_info(ip):
    """
    获取ip地址的信息
    """
    url = 'http://ip.taobao.com/outGetIpInfo'

    params = {
        'ip': ip,
        'accessKey': 'alibaba-inc'
    }
    res = requests.get(url, params)

    if not res.ok:
        res.raise_for_status()

    return res.json().get('data')


#
def get_domain_ip(domain):
    """
    获取ip地址
    """
    return socket.gethostbyname(domain)

if __name__ == '__main__':
    print(get_ip_info('221.218.209.125'))

