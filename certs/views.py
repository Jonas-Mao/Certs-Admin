# -*- coding: utf-8 -*-

import json
import re
import traceback
from datetime import datetime, timedelta
from dateutil.parser import parse as parse_date
from django.forms import model_to_dict
from django.http import JsonResponse
from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from certs.utils.certs_log import logger
from certs.serializers import CertsSerializer, CertTrusteeshipSerializer, CertTrusteeshipDeploySerializer
from certs.utils.custom_certs_filter_class import CertsFilter
from certs.utils import update_cert_addon_info
from django.utils.decorators import method_decorator
from certs_admin.utils import datetime_util
from certs_admin.utils.time_util import get_diff_days
from certs_admin.service import auth_service
from certs_admin.enums.role_enum import RoleEnum
from certs_admin.enums.status_enum import StatusEnum
from certs_admin.enums.deploy_status_enum import DeployStatusEnum
from certs_admin.service import issue_cert_service, cert_service
from certs_admin.enums.operation_enum import OperationEnum
from certs_admin.service.operation_service import class_operation_log_decorator, def_operation_log_decorator
from certs_admin.utils.django_ext.app_exception import DataNotFoundAppException
from envs.models import Envs
from hosts.models import Host
from certs.models import Certs, CertTrusteeship, CertTrusteeshipDeploy
from django.contrib.auth import get_user_model
User = get_user_model()


class CertsViewSet(ModelViewSet):
    """
    SSL证书
    """
    queryset = Certs.objects.all()
    serializer_class = CertsSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ('domain',)
    filterset_class = CertsFilter
    # filterset_fields = ('domain',) 

    @method_decorator(class_operation_log_decorator(
        model=Certs.objects,
        operation_type_id=OperationEnum.UPDATE,
        primary_key='id')
    )
    def update(self, request, pk=None, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            error = json.dumps(e.detail, ensure_ascii=False)
            error = re.sub(r'[\[\]{}"\s]', '', error)
            res = {'code': e.status_code, 'msg': error}
            return Response(res)
        self.perform_update(serializer)

        res = {'code': 200, 'id': pk, 'msg': '更新成功！'}
        return JsonResponse(res)

    @method_decorator(class_operation_log_decorator(
        model=Certs.objects,
        operation_type_id=OperationEnum.DELETE,
        primary_key='pk')
    )
    def destroy(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        res = {'code': 200, 'msg': '删除成功！'}
        return JsonResponse(res)

    @method_decorator(class_operation_log_decorator(
        model=Certs.objects,
        operation_type_id=OperationEnum.CREATE,
        primary_key='id')
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            error = json.dumps(e.detail, ensure_ascii=False)
            error = re.sub(r'[\[\]{}"\s]', '', error)   # 替换[]、{}、"和空格
            res = {'code': e.status_code, 'msg': error}
            return Response(res)
        self.perform_create(serializer)
        id = serializer.data.get('id')

        res = {'code': 200, 'id': id, 'msg': '添加成功！'}
        return JsonResponse(res)

    def perform_create(self, serializer):
        user = User.objects.get(id=self.request.data.get('user'))
        envs = Envs.objects.get(id=self.request.data.get('envs'))
        serializer.save(
            user=user,
            envs=envs
        )

    def perform_update(self, serializer):
        user = User.objects.get(id=self.request.data.get('user'))
        envs = Envs.objects.get(id=self.request.data.get('envs'))
        update_time = datetime_util.get_datetime()
        serializer.save(
            user=user,
            envs=envs,
            update_time=update_time
        )


class CertTrusteeshipViewSet(ModelViewSet):
    """
    托管证书
    """
    queryset = CertTrusteeship.objects.all()
    serializer_class = CertTrusteeshipSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ('domain',)
    filterset_fields = ('domain',)

    @method_decorator(class_operation_log_decorator(
        model=CertTrusteeship.objects,
        operation_type_id=OperationEnum.UPDATE,
        primary_key='id')
    )
    def update(self, request, pk=None, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            error = json.dumps(e.detail, ensure_ascii=False)
            error = re.sub(r'[\[\]{}"\s]', '', error)
            res = {'code': e.status_code, 'msg': error}
            return Response(res)
        self.perform_update(serializer)

        res = {'code': 200, 'id': pk, 'msg': '更新成功！'}
        return JsonResponse(res)

    @method_decorator(class_operation_log_decorator(
        model=CertTrusteeship.objects,
        operation_type_id=OperationEnum.DELETE,
        primary_key='pk')
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        res = {'code': 200, 'msg': '删除成功！'}
        return JsonResponse(res)

    @method_decorator(class_operation_log_decorator(
        model=CertTrusteeship.objects,
        operation_type_id=OperationEnum.CREATE,
        primary_key='id')
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            error = json.dumps(e.detail, ensure_ascii=False)
            error = re.sub(r'[\[\]{}"\s]', '', error)
            res = {'code': e.status_code, 'msg': error}
            return Response(res)
        self.perform_create(serializer)
        id = serializer.data.get('id')

        res = {'code': 200, 'id': id, 'msg': '添加成功！'}
        return JsonResponse(res)

    def perform_create(self, serializer):
        user = User.objects.get(id=self.request.data.get('user'))
        envs = Envs.objects.get(id=self.request.data.get('envs'))
        serializer.save(
            user=user,
            envs=envs,
            total_days=get_diff_days(
                parse_date(self.request.data.get('ssl_start_time')),
                parse_date(self.request.data.get('ssl_expire_time'))
            ),
            remaining_days=get_diff_days(
                datetime.now(),
                parse_date(self.request.data.get('ssl_expire_time'))
            )
        )

    def perform_update(self, serializer):
        user = User.objects.get(id=self.request.data.get('user'))
        envs = Envs.objects.get(id=self.request.data.get('envs'))
        update_time = datetime_util.get_datetime()
        serializer.save(
            user=user,
            envs=envs,
            update_time=update_time
        )


class CertTrusteeshipDeployViewSet(ModelViewSet):
    """
    托管证书部署
    """
    queryset = CertTrusteeshipDeploy.objects.all()
    serializer_class = CertTrusteeshipDeploySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ('deploy_type_id',)
    filterset_fields = ('deploy_type_id',)

    @method_decorator(class_operation_log_decorator(
        model=CertTrusteeshipDeploy.objects,
        operation_type_id=OperationEnum.UPDATE,
        primary_key='id')
    )
    def update(self, request, pk=None, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            error = json.dumps(e.detail, ensure_ascii=False)
            error = re.sub(r'[\[\]{}"\s]', '', error)
            res = {'code': e.status_code, 'msg': error}
            return Response(res)
        self.perform_update(serializer)

        res = {'code': 200, 'id': pk, 'msg': '更新成功！'}
        return JsonResponse(res)

    @method_decorator(class_operation_log_decorator(
        model=CertTrusteeshipDeploy.objects,
        operation_type_id=OperationEnum.DELETE,
        primary_key='pk')
    )
    def destroy(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        res = {'code': 200, 'msg': '删除成功！'}
        return JsonResponse(res)

    @method_decorator(class_operation_log_decorator(
        model=CertTrusteeshipDeploy.objects,
        operation_type_id=OperationEnum.CREATE,
        primary_key='id')
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            error = json.dumps(e.detail, ensure_ascii=False)
            error = re.sub(r'[\[\]{}"\s]', '', error)
            res = {'code': e.status_code, 'msg': error}
            return Response(res)
        self.perform_create(serializer)
        id = serializer.data.get('id')

        res = {'code': 200, 'id': id, 'msg': '添加成功！'}
        return JsonResponse(res)

    def perform_create(self, serializer):
        host = Host.objects.get(id=self.request.data.get('host'))
        cert_trusteeship = CertTrusteeship.objects.get(id=self.request.data.get('cert_trusteeship'))
        serializer.save(
            host=host,
            cert_trusteeship=cert_trusteeship
        )

    def perform_update(self, serializer):
        host = Host.objects.get(id=self.request.data.get('host'))
        cert_trusteeship = CertTrusteeship.objects.get(id=self.request.data.get('cert_trusteeship'))
        update_time = datetime_util.get_datetime()
        serializer.save(
            host=host,
            cert_trusteeship=cert_trusteeship,
            update_time=update_time
        )


@auth_service.permission(role=RoleEnum.USER)
def get_cert_trusteeship_deploy_row(request):
    """
    根据托管证书ID查询部署托管证书
    """
    cert_trusteeship_id = request.GET.get('cert_trusteeship')
    cert_trusteeship_deploy_row = CertTrusteeshipDeploy.objects.filter(cert_trusteeship__id=cert_trusteeship_id)

    cert_trusteeship_row = CertTrusteeship.objects.filter(id=cert_trusteeship_id)
    domain = ''
    for i in cert_trusteeship_row:
        domain = i.domain

    if cert_trusteeship_deploy_row:
        cert_trusteeship_deploy_list = []
        for i in cert_trusteeship_deploy_row:
            cert_trusteeship_deploy_dict = {}
            cert_trusteeship_deploy_dict['domain'] = domain
            cert_trusteeship_deploy_dict['id'] = i.id
            cert_trusteeship_deploy_dict['cert_trusteeship'] = model_to_dict(i.cert_trusteeship)
            cert_trusteeship_deploy_dict['host'] = model_to_dict(i.host)
            cert_trusteeship_deploy_dict['deploy_type_id'] = i.deploy_type_id
            cert_trusteeship_deploy_dict['deploy_key_file'] = i.deploy_key_file
            cert_trusteeship_deploy_dict['deploy_fullchain_file'] = i.deploy_fullchain_file
            cert_trusteeship_deploy_dict['deploy_reloadcmd'] = i.deploy_reloadcmd
            cert_trusteeship_deploy_dict['status'] = i.status
            cert_trusteeship_deploy_dict['create_time'] = i.create_time
            cert_trusteeship_deploy_dict['update_time'] = i.update_time
            cert_trusteeship_deploy_list.append(cert_trusteeship_deploy_dict)
    else:
        cert_trusteeship_deploy_list = []

    res = {'code': 200, 'data': cert_trusteeship_deploy_list, 'msg': '查询成功！'}
    return JsonResponse(res)


@auth_service.permission(role=RoleEnum.USER)
def deploy_cert_trusteeship_file(request):
    """
    SSH部署托管证书
    """
    data = json.loads(request.body)

    current_user_id = data.get('user') or 1
    cert_trusteeship_id = data.get('cert_trusteeship')
    deploy_key_file = data.get('deploy_key_file')
    deploy_fullchain_file = data.get('deploy_fullchain_file')
    deploy_host_id = data.get('deploy_host_id')
    deploy_reloadcmd = data.get('deploy_reloadcmd')
    id = data.get('id')

    host_row = Host.objects.filter(id=deploy_host_id)
    if not host_row:
        raise DataNotFoundAppException()

    cert_trusteeship_row = CertTrusteeship.objects.get(
        id=cert_trusteeship_id,
        user__id=current_user_id
    )
    if not cert_trusteeship_row and cert_trusteeship_row.ssl_cert:
        raise DataNotFoundAppException()

    try:
        issue_cert_service.deploy_cert_file(
            deploy_host_id=deploy_host_id,
            ssl_cert_key=cert_trusteeship_row.ssl_cert_key,
            ssl_cert=cert_trusteeship_row.ssl_cert,
            deploy_key_file=deploy_key_file,
            deploy_fullchain_file=deploy_fullchain_file,
            deploy_reloadcmd=deploy_reloadcmd
        )
        res = {'code': 200, 'msg': '部署成功！'}
    except Exception as e:
        err = e
        logger.error(traceback.format_exc())
        res = {'code': 500, 'msg': '部署失败 %s' % e}

    status = DeployStatusEnum.SUCCESS if res['code'] == 200 else DeployStatusEnum.ERROR

    CertTrusteeshipDeploy.objects.filter(
        id=id,
        cert_trusteeship__id=cert_trusteeship_id
    ).update(status=status)

    return JsonResponse(res)


@auth_service.permission(role=RoleEnum.USER)
@def_operation_log_decorator(
    model=Certs.objects,
    operation_type_id=OperationEnum.UPDATE,
    primary_key='cert_id',
    method='data'
)
def upate_cert_row(request):
    """
    单行更新按钮
    """
    cert_id = request.GET.get('cert_id')

    cert_row = Certs.objects.get(id=cert_id)
    if not cert_row:
        raise DataNotFoundAppException()

    data = update_cert_addon_info.cert_add_info(cert_row)

    res = {'code': 200, 'data': data, 'cert_id': cert_id, 'msg': '更新成功！'}
    return JsonResponse(res)


@auth_service.permission(role=RoleEnum.USER)
def cert_env_count(request):
    """
    分组证书数量
    """
    env_cert_dict = {}

    cert_env_res = Certs.objects.values('envs').annotate(count=Count(1)).order_by('envs')

    for env_count in cert_env_res:
        env_cert_dict[env_count['envs']] = env_count['count']
        # {"2": 2, "1": 1}  envs: count

    return JsonResponse({
        'code': 200,
        'msg': '获取成功',
        'data': env_cert_dict
    })


@auth_service.permission(role=RoleEnum.USER)
@def_operation_log_decorator(
    model=Certs.objects,
    operation_type_id=OperationEnum.UPDATE,
    primary_key='cert_id',
    method='data'
)
def update_cert_monitor(request):
    """
    更新是否监控
    """
    current_user_id = request.GET.get('user_id')
    cert_id = request.GET.get('cert_id')

    cert_row = Certs.objects.filter(id=cert_id, user__id=current_user_id)
    if not cert_row:
        raise DataNotFoundAppException()

    data = {
        "is_monitor": request.GET.get('is_monitor', StatusEnum.Enabled)
    }
    Certs.objects.filter(id=cert_id).update(**data)

    res = {'code': 200, 'cert_id': cert_id, 'msg': '更新成功！'}
    return JsonResponse(res)


@auth_service.permission(role=RoleEnum.USER)
@def_operation_log_decorator(
    model=Certs.objects,
    operation_type_id=OperationEnum.UPDATE,
    primary_key='cert_id',
    method='data'
)
def update_cert_auto_update(request):
    """
    更新自动更新
    """
    current_user_id = request.GET.get('user_id')
    cert_id = request.GET.get('cert_id')

    cert_row = Certs.objects.filter(id=cert_id, user__id=current_user_id)
    if not cert_row:
        raise DataNotFoundAppException()

    data = {
        "auto_update": request.GET.get('auto_update', StatusEnum.Enabled)
    }
    Certs.objects.filter(id=cert_id).update(**data)

    res = {'code': 200, 'cert_id': cert_id, 'msg': '更新成功！'}
    return JsonResponse(res)


@auth_service.permission(role=RoleEnum.USER)
def cert_expire_count(request):
    """
    过期证书数量
    """
    expire_count = Certs.objects.filter(
        remaining_days__lte=0
    ).count()

    return JsonResponse({
        'code': 200,
        'count': expire_count
    })


@auth_service.permission(role=RoleEnum.USER)
def certs_echart(request):
    """
    证书统计
    """
    now = datetime.now()
    end = (now + timedelta(45))

    # 已过期
    expire_data = Certs.objects.filter(
        Q(expire_time__lt=now) | Q(expire_time__isnull=True)
    ).count()

    # 即将过期
    soon_expire_data = Certs.objects.filter(
        expire_time__gt=now,
        expire_time__lt=end
    ).count()

    # 未过期
    success_data = Certs.objects.filter(
        expire_time__gt=end
    ).count()

    data = {
        'expire_data': expire_data,
        'soon_expire_data': soon_expire_data,
        'success_data': success_data
    }

    res = {'data': data, 'code': 200, 'msg': '获取成功！'}
    return JsonResponse(res)
