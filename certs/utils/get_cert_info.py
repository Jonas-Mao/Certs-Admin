# -*- coding: utf-8 -*-

import ssl, socket, json, requests, hmac, base64, hashlib, time
from datetime import datetime


def ips_count(domain):
    """
    主机数量
    """
    try:
        ips = socket.gethostbyname_ex(domain)[2]
        return len(ips)
    except:
        ips = 0
        return ips

def expire_info(domain, port):
    """
    证书时间
    """
    current_date = datetime.now()

    socket.setdefaulttimeout(15)
    context = ssl.create_default_context()

    try:
        conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=domain)
        conn.connect((domain, port))
        cert = conn.getpeercert()
        conn.close()
        # 证书颁发/过期时间
        not_before = cert['notBefore']
        not_after = cert['notAfter']
        issue_time = datetime.strptime(not_before, '%b %d %H:%M:%S %Y %Z')
        expire_time = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
    except:
        issue_time = None
        expire_time = None

    if issue_time and expire_time and expire_time > current_date:
        remaining_days = (expire_time - current_date).days
        total_days = (expire_time - issue_time).days
    else:
        remaining_days = 0
        total_days = 0

    data = {
        'issue_time': issue_time,
        'expire_time': expire_time,
        'remaining_days': remaining_days,
        'total_days': total_days
        }

    return data
