# -*- coding: utf-8 -*-

import socket
import ssl
import OpenSSL

from certs_admin.enums.ssl_type_enum import SSLTypeEnum
from certs_admin.utils import time_util
from files import domain_util
from certs_admin.utils.cert_util import cert_common

# 默认的SSL端口
DEFAULT_SSL_PORT = 443


def verify_cert(cert, domain):
    """
    验证证书和域名是否匹配
    """
    # 检查 颁发对象 域名（CN） 备用域名（SAN）
    common_name = cert.get_subject().commonName

    dns_names = cert_common.get_certificate_san(cert)

    if common_name not in dns_names:
        dns_names.insert(0, common_name)

    for dns_name in dns_names:
        domain_checked = domain_util.verify_cert_common_name(dns_name, domain)
        if domain_checked:
            return True

    return False


def get_ssl_cert(
        domain,
        host=None,
        port=443,
        timeout=3,
        ssl_type=SSLTypeEnum.SSL_TLS
):
    """
    不验证证书，仅验证域名
    支持通配符
    """

    # 默认参数
    host = host or domain

    # socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    sock.connect((host, port))

    if ssl_type == SSLTypeEnum.START_TLS:
        try:
            sock.recv(1000)
            sock.send('EHLO\nSTARTTLS\n'.encode('utf-8'))
            sock.recv(1000)
        except:
            pass

    # SSL
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    ssl_context.verify_mode = ssl.CERT_NONE
    ssl_context.check_hostname = False

    # fix: Python2 AttributeError: __exit__
    wrap_socket = ssl_context.wrap_socket(sock, server_hostname=domain)
    dercert = wrap_socket.getpeercert(True)
    wrap_socket.close()

    server_cert = ssl.DER_cert_to_PEM_cert(dercert)
    cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, server_cert.encode())
    return cert


def get_ssl_cert_by_openssl(
        domain,
        host=None,
        port=443,
        timeout=3,
        ssl_type=SSLTypeEnum.SSL_TLS
):
    """
    不验证证书，仅验证域名
    支持通配符
    """

    cert = get_ssl_cert(domain, host, port, timeout, ssl_type=ssl_type)

    # verify
    domain_checked = verify_cert(cert, domain)

    if not domain_checked:
        raise Exception("domain not verified")

    return {
        'start_date': time_util.parse_time(cert.get_notBefore().decode()),
        'expire_date': time_util.parse_time(cert.get_notAfter().decode()),
    }
