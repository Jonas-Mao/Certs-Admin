# -*- coding: utf-8 -*-

import json
from django.http import JsonResponse
from files import deploy_oss_cdn_dcdn_service
from certs_admin.utils.django_ext.app_exception import DataNotFoundAppException
from certs_admin.enums.deploy_status_enum import DeployStatusEnum
from certs_admin.enums.ssl_deploy_type_enum import SSLDeployTypeEnum
from apply_cert.models import ApplyCert


def deploy_cert_to_oss(request):
    """
    部署证书到阿里云OSS
    """
    current_user_id = request.session.get('_auth_user_id')

    data = json.loads(request.body)
    issue_cert_id = data.get('issue_cert_id')
    dns_id = data.get('dns_id')

    issue_cert_row = ApplyCert.objects.filter(
        id=issue_cert_id,
        user__id=current_user_id
    )

    if not issue_cert_row:
        raise DataNotFoundAppException()

    res = deploy_oss_cdn_dcdn_service.deploy_cert_to_oss(
        issue_cert_id=issue_cert_id,
        dns_id=dns_id,
    )

    # 更新验证信息
    data = {
        "deploy_type_id": SSLDeployTypeEnum.OSS,
        "deploy_host_id": dns_id,
        "ssl_deploy_status": DeployStatusEnum.SUCCESS
    }

    ApplyCert.objects.filter(id=issue_cert_id).update(
        deploy_type_id=SSLDeployTypeEnum.OSS,
        deploy_host_id=dns_id,
        ssl_deploy_status=DeployStatusEnum.SUCCESS
    )

    # 验证成功后, check_auto_renew
    deploy_oss_cdn_dcdn_service.check_auto_renew(
        issue_cert_id=issue_cert_id
    )

    return JsonResponse(
        {
            'code': 200,
            'msg': '部署证书到OSS成功！',
            'data': res
        })

def deploy_cert_to_cdn(request):
    """
    部署证书到阿里云CDN
    """
    current_user_id = request.session.get('_auth_user_id')

    data = json.loads(request.body)
    issue_cert_id = data.get('issue_cert_id')
    dns_id = data.get('dns_id')

    issue_cert_row = ApplyCert.objects.filter(
        id=issue_cert_id,
        user__id=current_user_id
    )

    if not issue_cert_row:
        raise DataNotFoundAppException()

    res = deploy_oss_cdn_dcdn_service.deploy_cert_to_cdn(
        issue_cert_id=issue_cert_id,
        dns_id=dns_id,
    )

    # 更新验证信息
    ApplyCert.objects.filter(id=issue_cert_id).update(
        deploy_type_id=SSLDeployTypeEnum.CDN,
        deploy_host_id=dns_id,
        ssl_deploy_status=DeployStatusEnum.SUCCESS
    )

    # 验证成功后, check_auto_renew
    deploy_oss_cdn_dcdn_service.check_auto_renew(
        issue_cert_id=issue_cert_id
    )

    return JsonResponse(
        {
            'code': 200,
            'msg': '部署证书到CDN成功！',
            'data': res
        })

def deploy_cert_to_dcdn(request):
    """
    部署证书到阿里云DCDN
    """
    current_user_id = request.session.get('_auth_user_id')

    data = json.loads(request.body)
    issue_cert_id = data.get('issue_cert_id')
    dns_id = data.get('dns_id')

    issue_cert_row = ApplyCert.objects.filter(
        id=issue_cert_id,
        user__id=current_user_id
    )

    if not issue_cert_row:
        raise DataNotFoundAppException()

    res = deploy_oss_cdn_dcdn_service.deploy_cert_to_dcdn(
        issue_cert_id=issue_cert_id,
        dns_id=dns_id,
    )

    # 更新验证信息
    ApplyCert.objects.filter(id=issue_cert_id).update(
        deploy_type_id=SSLDeployTypeEnum.DCDN,
        deploy_host_id=dns_id,
        ssl_deploy_status=DeployStatusEnum.SUCCESS
    )

    # 验证成功后, check_auto_renew
    deploy_oss_cdn_dcdn_service.check_auto_renew(
        issue_cert_id=issue_cert_id
    )

    return JsonResponse(
        {
            'code': 200,
            'msg': '部署证书到DCDN成功！',
            'data': res
        })