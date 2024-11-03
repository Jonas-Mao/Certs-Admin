# -*- coding: utf-8 -*-

from certs_admin.utils import datetime_util
from certs.models import Certs
from certs.utils.get_cert_addon_info import certs_expire, cert_ips, certs_root_domain, certs_status


# ******
def cert_add_info(domain_row):
    """
    证书附加信息
    """
    ssl_expire = certs_expire(domain_row.domain, domain_row.port)
    ips = cert_ips(domain_row.domain)
    root_domain = certs_root_domain(domain_row.domain)
    status = certs_status(domain_row.domain, domain_row.port)

    error = ''
    try:
        Certs.objects.filter(domain=domain_row.domain).update(
            ips_count=ips,
            root_domain=root_domain,
            status=status,
            issue_time=ssl_expire.get('issue_time'),
            expire_time=ssl_expire.get('expire_time'),
            remaining_days=ssl_expire.get('remaining_days'),
            total_days=ssl_expire.get('total_days'),
            update_time = datetime_util.get_datetime()
        )
    except Exception as e:
        print(e)
