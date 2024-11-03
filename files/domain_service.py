# -*- coding: utf-8 -*-

import time
import traceback
from datetime import datetime
from certs_admin.utils import datetime_util, cert_util, time_util
from files import domain_util
from certs_admin.utils.cert_util import cert_socket_v2, cert_openssl_v2
from certs_admin.utils.django_ext.app_exception import ForbiddenAppException
from django.db.models import Count
from certs_admin.log import loggers
from domain_ipaddr.models import DomainInfo, DomainIpAddr
from django.contrib.auth import get_user_model
User = get_user_model()


def update_domain_host_list(domain_row):
    """
    更新IP信息
    """
    domain_host_list = []

    try:
        domain_host_list = cert_socket_v2.get_domain_host_list(
            domain=domain_row.domain,
            port=domain_row.port
        )
    except Exception as e:
        print('更新IP信息失败%s' %e)

    lst = [
        {
            'domain_id': domain_row.id,
            'host': domain_host
        } for domain_host in domain_host_list]

    objects = [
        DomainIpAddr(
            domain_id=item['domain_id'],
            host=item['host']
        ) for item in lst
    ]

    DomainIpAddr.objects.bulk_create(objects)


def update_domain_address_list_cert(domain_row):
    """
    更新证书信息
    """
    lst = DomainIpAddr.objects.get(domain_id=domain_row.id)

    err = ''
    for address_row in lst:
        err = update_address_row_info_wrap(address_row, domain_row)

    sync_address_info_to_domain_info(domain_row)
    return err


def update_address_row_info_wrap(address_row, domain_row):
    """
    更新单个地址信息的代理方法 增加重试次数
    """
    MAX_RETRY_COUNT = 3     # 最大重试次数

    retry_count = 0

    err = ''

    while True:
        retry_count += 1

        err = update_address_row_info(address_row, domain_row)

        if not err or retry_count >= MAX_RETRY_COUNT:
            break

        time.sleep(0.5)

    return err


def update_address_row_info(address_row, domain_row):
    """
    更新单个地址信息
    """

    # 获取证书信息
    cert_info = {}

    err = ''
    try:
        cert_info = cert_openssl_v2.get_ssl_cert_by_openssl(
            domain=domain_row.domain,
            host=address_row.host,
            port=domain_row.port,
            ssl_type=domain_row.ssl_type
        )
    except Exception as e:
        err = e.__str__()
        loggers.error(traceback.format_exc())

    loggers.info(cert_info)

    try:
        DomainIpAddr.objects.filter(id=address_row.id).update(
            ssl_start_time=cert_info.get('start_date'),
            ssl_expire_time=cert_info.get('expire_date'),
            ssl_remaining_days=time_util.get_diff_days(cert_info.get('start_date'), cert_info.get('expire_date')),
            update_time=datetime_util.get_datetime()
        )
    except Exception as e:
        err = e.__str__()
        loggers.error(traceback.format_exc())

    return err


def update_address_row_info_with_sync_domain_row(address_id):
    """
    更新主机信息并同步到与域名表
    """
    address_row = DomainIpAddr.objects.get(address_id)

    domain_row = DomainInfo.objects.get(address_row.domain_id)

    update_address_row_info_wrap(address_row, domain_row)

    sync_address_info_to_domain_info(domain_row)


def sync_address_info_to_domain_info(domain_row):
    """
    同步主机信息到域名信息表
    """
    first_address_row = DomainIpAddr.objects.get(domain_id=domain_row.id).order_by('ssl_expire_days')

    connect_status = False

    if first_address_row is None:
        DomainIpAddr.objects.filter(domain_id=domain_row.id).update(
            sl_start_time=None,
            ssl_expire_time=None
        )
    elif first_address_row.ssl_remaining_days > 0:
        connect_status = True

    DomainInfo.objects.filter(id=domain_row.id).update(
        start_time=first_address_row.ssl_start_time,
        expire_time=first_address_row.ssl_expire_time,
        expire_days=first_address_row.ssl_remaining_days,
        connect_status=connect_status,
        update_time=datetime_util.get_datetime()
    )


def update_domain_row(domain_row):
    """
    更新域名相关数据
    """
    if not domain_row.root_domain:
        DomainInfo.objects.filter(id=domain_row.id).update(
            root_domain=domain_util.get_root_domain(domain_row.domain)
        )

    # 主机IP信息
    update_domain_host_list(domain_row)

    # 证书信息
    update_domain_address_list_cert(domain_row)


def get_cert_info(domain):
    """
    :param domain: str
    """
    now = datetime.now()
    info = {}
    expire_days = 0
    total_days = 0
    connect_status = True

    try:
        info = cert_util.get_cert_info(domain)

    except Exception:
        connect_status = False

    start_date = info.get('start_date')
    expire_date = info.get('expire_date')

    if start_date and expire_date:
        start_time = datetime_util.parse_datetime(start_date)
        expire_time = datetime_util.parse_datetime(expire_date)

        expire_days = (expire_time - now).days
        total_days = (expire_time - start_time).days

    return {
        'start_date': start_date,
        'expire_date': expire_date,
        'expire_days': expire_days,
        'total_days': total_days,
        'connect_status': connect_status,
        'info': info,
    }


def update_all_domain_cert_info():
    """
    更新所有域名信息
    """
    rows = DomainInfo.objects.get(auto_update=True).order_by('expire_days')

    for row in rows:
        try:
            update_domain_row(row)
        except Exception as e:
            print('更新域名信息失败%s' %e)


def update_all_domain_cert_info_of_user(user_id):
    """
    更新用户的所有证书信息
    """
    rows = DomainInfo.objects.filter(
        user__id=user_id,
        auto_update=True
    )

    for row in rows:
        update_domain_row(row)


def get_domain_info_list(user_id=None):

    user_row = User.objects.get(id=user_id)

    DomainInfo.objects.get(
        user__id=user_id,
        is_monitor=True,
        expire_days__lt=user_row.before_expire_days
    ).order_by(
        'expire_days',
        '-id'
    )


def check_permission_and_get_row(domain_id, user_id):
    """
    权限检查
    """
    row = DomainInfo.objects.get(id=domain_id)

    if row.user_id != user_id:
        raise ForbiddenAppException()

    return row


def load_domain_expire_days(lst):
    """
    加载域名过期时间字段 Number or None
    """
    root_domains = [row['root_domain'] for row in lst]

    domain_info_rows = DomainInfo.objects.filter(domain__contains=root_domains)

    domain_info_map = {
        row.domain: row.real_domain_expire_days
        for row in domain_info_rows
    }

    for row in lst:
        row['domain_expire_days'] = domain_info_map.get(row['root_domain'])

    return lst


def load_address_count(lst):
    """
    加载主机数量字段
    """
    row_ids = [row['id'] for row in lst]

    address_groups = DomainIpAddr.objects.values('domain_id').annotate(
        count=Count('id')
    ).only(
        'domain_id',
        'count'
    ).get(domain_id__in=row_ids)

    address_group_map = {
        str(row.domain_id): row.count
        for row in address_groups
    }

    for row in lst:
        row['address_count'] = address_group_map.get(str(row['id']), 0)

    return lst


def init_domain_cert_info_of_user(user_id):
    """
    初始化证书信息
    """
    rows = DomainInfo.objects.get(user__id=user_id)

    for row in rows:
        update_domain_row(row)
