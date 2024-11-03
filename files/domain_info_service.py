# -*- coding: utf-8 -*-

import time
from datetime import datetime, timedelta
from rest_framework.response import Response
from domain_ipaddr.models import DomainInfo
from django.http import JsonResponse
from certs_admin.utils import datetime_util, time_util
from files.whois_util import whois_util
from files import domain_icp_service


#
def add_domain_info(
        domain,
        user,
        envs,
        auto_update,
        comment='',
        icp_company='',
        icp_licence='',
        domain_start_time = None,
        domain_expire_time = None
):

    domain_info = DomainInfo.objects.filter(domain=domain)
    if domain_info:
        res = {'code': 500,'msg': '%s已存在！' % domain}
        return Response(res)

    # 添加域名监测
    try:
        domain_info_row = DomainInfo.objects.create(
            domain=domain,
            user=user,
            envs=envs,
            auto_update=auto_update,
            comment=comment,
            icp_company=icp_company,
            icp_licence=icp_licence,
            domain_start_time=domain_start_time,
            domain_expire_time=domain_expire_time
        )
    except Exception as e:
        return e

    # 添加时自动更新
    if auto_update:
        update_domain_info_row(domain_info_row)

    # # 添加的时候顺便添加icp备案信息
    # update_domain_row_icp(domain_info_row)        # 没找到免费的ICP备案接口API

    return Response(
            {
                'code': 200,
                'msg': '域名信息添加成功！',
                'data': domain_info_row
            })


#
def update_domain_info_row(row):
    """
    更新一行数据
    """
    domain_whois = None

    try:
        domain_whois = whois_util.get_domain_info(row.domain)
    except Exception as e:
        # 增加容错
        try:
            time.sleep(3)
            domain_whois = whois_util.get_domain_info(row.domain)
        except Exception as e:
            pass

    if domain_whois:
        DomainInfo.objects.filter(
            domain=row.domain
        ).update(
            domain_start_time=domain_whois['start_time'],
            domain_expire_time=domain_whois['expire_time'],
            domain_registrar=domain_whois['registrar'],
            domain_registrar_url=domain_whois['registrar_url'],
            update_time=datetime_util.get_datetime(),
            domain_expire_days=time_util.get_diff_days(datetime.now(), domain_whois['expire_time'])
        )

    return JsonResponse(
        {
            'code': 200,
            'msg': '更新数据成功！'
        })


def update_domain_row_icp(row):
    """
    更新ICP信息
    """
    item = domain_icp_service.get_domain_icp(domain=row.domain)

    if not item:
        return

    data = {}

    if not row.icp_company:
        data['icp_company'] = item.name

    if not row.icp_licence:
        data['icp_licence'] = item.icp

    if len(data) == 0:
        return

    try:
        DomainInfo.objects.filter(domain=row.domain).update(**data)
    except Exception as e:
        print('更新Domian Info失败%s' %e)

    return JsonResponse(
        {
            'code': 200,
            'msg': '更新ICP信息成功！'
        })


#
def update_all_domain_info():
    """
    更新所有的域名信息
    """
    now = datetime.now()

    notify_expire_time = now + timedelta(days=30)

    rows = DomainInfo.objects.filter(
        is_auto_update = True,
        domain_expire_time__lte=notify_expire_time      # 域名注册完后，过期时间基本不会改变，不用每次全量更新
    ).order_by('domain_expire_days')

    for row in rows:
        update_domain_info_row(row)

    return JsonResponse(
        {
            'code': 200,
            'msg': '更新所有域名信息成功！'
        })
