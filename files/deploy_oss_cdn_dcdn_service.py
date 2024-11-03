# -*- coding: utf-8 -*-

from certs_admin.utils.django_ext.app_exception import AppException
from certs_admin.utils.open_api import aliyun_oss_api, aliyun_cdn_api, aliyun_dcdn_api
from apply_cert.models import ApplyCert
from dnss.models import Dns


def deploy_cert_to_oss(issue_cert_id, dns_id):
    """
    部署SSL证书到OSS
    """
    issue_cert_row = ApplyCert.objects.get(id=issue_cert_id)

    if not issue_cert_row:
        raise AppException('证书数据不存在')

    dns_row = Dns.objects.get(id=dns_id)

    if not dns_row:
        raise AppException('DNS数据不存在')

    domain = issue_cert_row.domains[0]

    oss_info = aliyun_oss_api.cname_to_oss_info(domain)

    if not oss_info:
        raise AppException('DNS未设置')

    aliyun_oss_api.put_bucket_cname(
        access_key_id=dns_row.access_key,
        access_key_secret=dns_row.secret_key,
        bucket_name=oss_info['bucket_name'],
        domain=domain,
        certificate=issue_cert_row.ssl_certificate,
        private_key=issue_cert_row.ssl_certificate_key,
        endpoint=oss_info['endpoint'],
    )


def deploy_cert_to_cdn(issue_cert_id, dns_id):
    """
    部署SSL证书到CDN
    """
    issue_cert_row = ApplyCert.objects.get(id=issue_cert_id)

    if not issue_cert_row:
        raise AppException('证书数据不存在')

    dns_row = Dns.objects.get(id=dns_id)

    if not dns_row:
        raise AppException('DNS数据不存在')

    domain = issue_cert_row.domains[0]

    aliyun_cdn_api.set_cdn_domain_ssl_certificate_v2(
        access_key_id=dns_row.access_key,
        access_key_secret=dns_row.secret_key,
        domain_name=domain,
        certificate=issue_cert_row.ssl_certificate,
        private_key=issue_cert_row.ssl_certificate_key,
    )


def deploy_cert_to_dcdn(issue_cert_id, dns_id):
    """
    部署SSL证书到DCDN
    """
    issue_cert_row = ApplyCert.objects.get(id=issue_cert_id)

    if not issue_cert_row:
        raise AppException('证书数据不存在')

    dns_row = Dns.objects.get(id=dns_id)

    if not dns_row:
        raise AppException('DNS数据不存在')

    domain = issue_cert_row.domains[0]

    aliyun_dcdn_api.set_dcdn_domain_ssl_certificate(
        access_key_id=dns_row.access_key,
        access_key_secret=dns_row.secret_key,
        domain_name=domain,
        certificate=issue_cert_row.ssl_certificate,
        private_key=issue_cert_row.ssl_certificate_key,
    )


def check_auto_renew(issue_cert_id):
    """
    首次申请，自动判断是否可以自动续期
    :param issue_certificate_id:
    :return:
    """
    issue_cert_row = ApplyCert.objects.get(issue_cert_id)

    if issue_cert_row.can_auto_renew:
        ApplyCert.objects.filter(
            id=issue_cert_id
        ).update(
            is_auto_renew=True
        )