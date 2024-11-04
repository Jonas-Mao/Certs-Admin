# -*- coding: utf-8 -*-

import time
import traceback
from certs.utils.certs_log import logger
from certs.utils import update_cert_addon_info
from files import domain_util
from certs_admin.utils.cert_util import cert_openssl_v2, cert_common
from certs_admin.enums.deploy_status_enum import DeployStatusEnum
from certs.models import Certs, CertTrusteeshipDeploy


def get_cert_information(domain):
    """
    获取域名证书信息
    """
    resolve_domain = domain_util.parse_domain(domain)

    cert = cert_openssl_v2.get_ssl_cert(resolve_domain)
    parsed_cert = cert_common.parse_cert(cert)
    cert_pem = cert_common.dump_certificate_to_pem(cert)
    cert_text = cert_common.dump_certificate_to_text(cert)

    return {
        'resolve_domain': resolve_domain,
        'parsed_cert': parsed_cert.to_dict() if parsed_cert else parsed_cert,
        'cert_pem': cert_pem,
        'cert_text': cert_text,
    }


def update_all_cert():
    """
    更新所有证书信息
    """
    cert_rows = Certs.objects.filter(auto_update=1).order_by('expire_time')

    for row in cert_rows:
        try:
            update_cert_addon_info.cert_add_info(row)
        except Exception as e:
            logger.error(traceback.format_exc())

        time.sleep(0.5)
