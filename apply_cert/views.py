# -*- coding: utf-8 -*-

import json
from django_filters.rest_framework import DjangoFilterBackend
from django.http import JsonResponse
from django.forms import model_to_dict
from rest_framework.viewsets import ModelViewSet
from rest_framework import filters
from certs_admin.service import issue_cert_service
from django.utils.decorators import method_decorator
from certs_admin.enums.operation_enum import OperationEnum
from certs_admin.service.operation_service import class_operation_log_decorator, def_operation_log_decorator
from certs_admin.utils.acme_util.key_type_enum import KeyTypeEnum, KEY_TYPE_OPTIONS
from certs_admin.utils.acme_util.directory_type_enum import DirectoryTypeEnum, DIRECTORY_URL_OPTIONS
from certs_admin.utils import validate_util, fabric_util
from files import ip_util, domain_util
from certs_admin.utils.django_ext.app_exception import AppException, DataNotFoundAppException
from certs_admin.enums.deploy_status_enum import DeployStatusEnum
from certs_admin.enums.ssl_deploy_type_enum import SSLDeployTypeEnum
from certs_admin.enums.status_enum import StatusEnum
from certs_admin.service import auth_service
from certs_admin.enums.role_enum import RoleEnum
from apply_cert.utils.custom_certs_filter_class import ApplyCertFilter
from apply_cert.serializers import ApplyCertsSerializer
from apply_cert.models import ApplyCert
from certs.models import Certs
from hosts.models import Host
from envs.models import Envs
from django.contrib.auth import get_user_model
User = get_user_model()


class ApplyCertViewSet(ModelViewSet):
    """
    证书申请
    """
    queryset = ApplyCert.objects.all()
    serializer_class = ApplyCertsSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ('domains',)
    filterset_class = ApplyCertFilter

    @method_decorator(class_operation_log_decorator(
        model=ApplyCert.objects,
        operation_type_id=OperationEnum.DELETE,
        primary_key='pk')
    )
    def destroy(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        res = {'code': 200, 'msg': '删除成功！'}
        return JsonResponse(res)


@auth_service.permission(role=RoleEnum.USER)
def single_apply_cert(request):
    """
    查询单条数据
    """
    issue_cert_id = request.GET.get('issue_cert_id')
    data = ApplyCert.objects.get(id=issue_cert_id)
    data = model_to_dict(data)

    res = {'code': 200, 'msg': '查询成功！', 'data': data}
    return JsonResponse(res)


@auth_service.permission(role=RoleEnum.USER)
@def_operation_log_decorator(
    model=ApplyCert.objects,
    operation_type_id=OperationEnum.CREATE,
    primary_key='id')
def issue_cert(request):
    """
    提交申请证书
    """
    data = json.loads(request.body)

    current_user_id = data.get('user_id') or 1
    directory_type = data.get('directory_type') or DirectoryTypeEnum.LETS_ENCRYPT
    key_type = data.get('key_type') or KeyTypeEnum.RSA
    domains = data.get('domains')
    user_obj = User.objects.get(id=current_user_id)

    issue_cert_row = issue_cert_service.issue_cert(
        user=user_obj,
        domains=domains,
        directory_type=directory_type,
        key_type=key_type
    )

    res = {'code': 200, 'id': issue_cert_row.id, 'msg': '提交成功！'}
    return JsonResponse(res)


@auth_service.permission(role=RoleEnum.USER)
def deploy_verify_file(request):
    """
    部署验证文件
    """
    data = json.loads(request.body)

    current_user_id = data.get('user') or 1
    issue_cert_id = data.get('issue_cert_id')
    challenges = data.get('challenges')
    challenge_deploy_verify_path = data.get('challenge_deploy_verify_path')
    challenge_deploy_host_id = data.get('challenge_deploy_host_id')

    if not challenge_deploy_verify_path.endswith("/"):
        raise AppException("challenge_deploy_verify_path must endswith '/'")

    issue_cert_row = ApplyCert.objects.filter(
        id=issue_cert_id,
        user__id=current_user_id
    )
    if not issue_cert_row:
        raise DataNotFoundAppException()

    res = issue_cert_service.deploy_verify_file(
        challenge_deploy_host_id=challenge_deploy_host_id,
        challenge_deploy_verify_path=challenge_deploy_verify_path,
        challenges=challenges
    )
    result = json.loads(res.content.decode('utf-8'))
    auth_type = result.get('auth_type')

    ApplyCert.objects.filter(id=issue_cert_id).update(
        challenge_deploy_type_id=auth_type,
        challenge_deploy_host_id=challenge_deploy_host_id,
        challenge_deploy_verify_path=challenge_deploy_verify_path,
        challenge_deploy_status=DeployStatusEnum.SUCCESS
    )

    res = {'code': 200, 'msg': '部署成功！'}
    return JsonResponse(res)


@auth_service.permission(role=RoleEnum.USER)
def verify_cert(request):
    """
    验证域名
    """
    data = json.loads(request.body)

    current_user_id = data.get('user') or 1
    issue_cert_id = data.get('issue_cert_id')
    challenge_type = data.get('challenge_type')

    user_obj = User.objects.get(id=int(current_user_id))
    env_obj = Envs.objects.get(id=int(1))

    issue_cert_row = ApplyCert.objects.get(
        id=issue_cert_id,
        user__id=current_user_id
    )
    if not issue_cert_row:
        raise DataNotFoundAppException()

    issue_cert_service.verify_cert(issue_cert_id, challenge_type)
    issue_cert_service.renew_cert(issue_cert_id)

    # 验证成功，添加到证书监控
    lst = [
        {
            'domain': domain,
            'root_domain': domain_util.get_root_domain(domain),
            'port': 443,
            'user': user_obj
        }
        for domain in (json.loads(issue_cert_row.domains))
        if validate_util.is_domain(domain)
    ]

    for i in lst:
        domain = i['domain']
        cert = Certs.objects.filter(domain=domain)
        if cert:
            lst_set = [v for v in lst if domain not in v['domain']]
            lst = lst_set

    objects = [
        Certs(
            domain=item['domain'],
            root_domain=item['root_domain'],
            port=item['port'],
            user=item['user'],
            envs=env_obj
        )
        for item in lst
    ]

    Certs.objects.bulk_create(objects)

    res = {'code': 200, 'msg': '验证成功！',}
    return JsonResponse(res)


@auth_service.permission(role=RoleEnum.USER)
def get_cert_challenges(request):
    """
    获取验证方式
    """
    current_user_id = request.GET.get('user')
    issue_cert_id = request.GET.get('issue_cert_id')

    issue_cert_row = ApplyCert.objects.filter(
        id=issue_cert_id,
        user__id=current_user_id
    )
    if not issue_cert_row:
        raise DataNotFoundAppException()

    data = issue_cert_service.get_cert_challenges(issue_cert_id)
    data = data.content.decode('utf-8')

    res = {'code': 200, 'data': data, 'msg': '获取成功！'}
    return JsonResponse(res)


@auth_service.permission(role=RoleEnum.USER)
def get_allow_commands(request):
    """
    命令白名单
    """
    res = {'code': 200, 'data': fabric_util.allow_commands, 'msg': '获取成功！'}
    return JsonResponse(res)


@auth_service.permission(role=RoleEnum.USER)
def deploy_cert_file(request):
    """
    SSH方式部署证书
    """
    data = json.loads(request.body)

    current_user_id = data.get('user') or 1
    issue_cert_id = data.get('issue_cert_id')
    deploy_key_file = data.get('deploy_key_file')
    deploy_fullchain_file = data.get('deploy_fullchain_file')
    deploy_host_id = data.get('deploy_host_id')
    deploy_reloadcmd = data.get('deploy_reloadcmd')

    host_row = Host.objects.filter(id=deploy_host_id)
    if not host_row:
        raise DataNotFoundAppException()

    issue_cert_row = ApplyCert.objects.get(id=issue_cert_id, user__id=current_user_id)
    if not issue_cert_row:
        raise DataNotFoundAppException()
    if not issue_cert_row.ssl_cert:
        issue_cert_service.renew_cert(issue_cert_id)

    issue_cert_service.deploy_cert_file(
        deploy_host_id=deploy_host_id,
        ssl_cert_key=issue_cert_row.ssl_cert_key,
        ssl_cert=issue_cert_row.ssl_cert,
        deploy_key_file=deploy_key_file,
        deploy_fullchain_file=deploy_fullchain_file,
        deploy_reloadcmd=deploy_reloadcmd
    )
    ApplyCert.objects.filter(id=issue_cert_id).update(
        deploy_type_id=SSLDeployTypeEnum.SSH,
        deploy_host_id=deploy_host_id,
        deploy_key_file=deploy_key_file,
        deploy_fullchain_file=deploy_fullchain_file,
        deploy_reloadcmd=deploy_reloadcmd,
        deploy_status=DeployStatusEnum.SUCCESS
    )
    # 验证成功后, check_auto_renew
    issue_cert_service.check_auto_renew(issue_cert_id=issue_cert_id)

    res = {'code': 200, 'msg': '部署成功！'}
    return JsonResponse(res)


@def_operation_log_decorator(
    model=ApplyCert.objects,
    operation_type_id=OperationEnum.UPDATE,
    primary_key='issue_cert_id',
    method='data'
)
@auth_service.permission(role=RoleEnum.USER)
def update_auto_renew(request):
    """
    自动更新字段
    """
    current_user_id = request.GET.get('user')
    issue_cert_id = request.GET.get('issue_cert_id')
    is_auto_renew = request.GET.get('is_auto_renew', StatusEnum.Disabled)

    issue_cert_row = ApplyCert.objects.filter(
        id=issue_cert_id,
        user__id=current_user_id
    )
    if not issue_cert_row:
        raise DataNotFoundAppException()

    if issue_cert_row and issue_cert_row.can_auto_renew:
        ApplyCert.objects.filter(id=issue_cert_id).update(is_auto_renew=is_auto_renew)
    else:
        raise AppException("不支持自动续期！")

    res = {'code': 200, 'issue_cert_id': issue_cert_id, 'msg': '更新成功！'}
    return JsonResponse(res)


@auth_service.permission(role=RoleEnum.USER)
def renew_cert(request):
    """
    保存证书到数据库
    """
    current_user_id = request.GET.get('user')
    issue_cert_id = request.GET.get('issue_cert_id')

    issue_cert_row = ApplyCert.objects.filter(id=issue_cert_id, user__id=current_user_id)
    if not issue_cert_row:
        raise DataNotFoundAppException()

    issue_cert_service.renew_cert(issue_cert_id)

    res = {'code': 200, 'msg': '保存成功！'}
    return JsonResponse(res)


@auth_service.permission(role=RoleEnum.USER)
def renew_issue_cert(request):
    """
    续期按钮
    """
    current_user_id = request.GET.get('user')
    issue_cert_id = request.GET.get('issue_cert_id')

    issue_cert_row = ApplyCert.objects.get(
        id=issue_cert_id,
        user__id=current_user_id
    )
    if not issue_cert_row:
        raise DataNotFoundAppException()

    issue_cert_service.renew_cert_row(issue_cert_row)

    res = dict(code=200, msg='续期成功！')
    return JsonResponse(res)


def get_domain_host(request):
    """
    解析域名IP
    """
    data = json.loads(request.body)
    domain = data.get('domain')
    host = ip_util.get_domain_ip(domain)

    res = {'code': 200, 'data': {'domain': domain, 'host': host}, 'msg': '获取成功！'}
    return JsonResponse(res)


def get_issue_cert_options():
    """
    获取常量
    """
    return {
        'KEY_TYPE_OPTIONS': KEY_TYPE_OPTIONS,
        'DIRECTORY_URL_OPTIONS': DIRECTORY_URL_OPTIONS
    }

