# -*- coding: utf-8 -*-

import traceback
from .cert_socket import get_cert_info as get_cert_info_by_socket
import logging
logger = logging.getLogger('certs-admin')


def get_cert_info(domain_with_port):
    """
    工厂方法
    :param domain_with_port:
    """
    cert_info = None

    try:
        cert_info = get_cert_info_by_socket(domain_with_port)
    except:
        logger.error(traceback.format_exc())

    return cert_info
