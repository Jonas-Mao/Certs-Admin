# -*- coding: utf-8 -*-

import json
from django.utils.decorators import method_decorator
from certs_admin.enums.operation_enum import OperationEnum
from certs_admin.service.operation_service import class_operation_log_decorator, def_operation_log_decorator
from certs_admin.service import notify_service, auth_service
from certs_admin.utils import datetime_util
from certs_admin.utils.django_ext.app_exception import DataNotFoundAppException
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework import filters
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from notify.models import Notify
from envs.models import Envs
from notify.serializers import NotifySerializer
from django.contrib.auth import get_user_model
User = get_user_model()

from certs_admin.service import issue_cert_service
from certs_admin.enums.ssl_deploy_type_enum import SSLDeployTypeEnum
from certs_admin.enums.deploy_status_enum import DeployStatusEnum
from apply_cert.models import ApplyCert
from django.forms import model_to_dict


class NotifyViewSet(ModelViewSet):
    """
    通知管理
    """
    queryset = Notify.objects.all()
    serializer_class = NotifySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]  # 指定过滤器
    search_fields = ('title',)
    filter_fields = ('title',)

    @method_decorator(class_operation_log_decorator(
        model=Notify.objects,
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
            pass

        title = request.data.get('title')
        notify_choice = request.data.get('notify_choice', 1)
        event_id = request.data.get('event_id')
        expire_days = request.data.get('expire_days', 0)
        value_raw = request.data.get('value_raw')
        user_obj = User.objects.get(id=request.user.id)
        envs_id = request.data.get('envs')

        # 执行操作
        notify_obj = Notify.objects.get(title=title)
        notify_obj.title = title
        notify_obj.notify_choice = notify_choice
        notify_obj.event_id = event_id
        notify_obj.expire_days = expire_days
        notify_obj.value_raw = value_raw
        notify_obj.user = user_obj
        notify_obj.envs.add(*envs_id)
        notify_obj.update_time = datetime_util.get_datetime()
        notify_obj.save()

        res = {'code': 200, 'id': pk, 'msg': '更新成功！'}
        return JsonResponse(res)

    @method_decorator(class_operation_log_decorator(
        model=Notify.objects,
        operation_type_id=OperationEnum.DELETE,
        primary_key='pk')
    )
    def destroy(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        res = {'code': 200, 'msg': '删除成功！'}
        return JsonResponse(res)

    @method_decorator(class_operation_log_decorator(
        model=Notify.objects,
        operation_type_id=OperationEnum.CREATE,
        primary_key='id')
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            pass

        title = request.data.get('title')
        notify_choice = request.data.get('notify_choice', 1)
        event_id = request.data.get('event_id')
        expire_days = request.data.get('expire_days', 0)
        value_raw = request.data.get('value_raw')
        user_obj = User.objects.get(id=request.data.get('user'))

        try:
            notify_obj = Notify.objects.create(
                title = title.strip(),
                notify_choice=notify_choice,
                event_id=event_id,
                expire_days=expire_days,
                value_raw=value_raw,
                user=user_obj
            )
            # 多对多
            envs_id = request.data.get('envs')
            for id in envs_id:
                env_obj = Envs.objects.get(id=id)
                notify_obj.envs.add(env_obj)
            res = {'code': 200, 'id': notify_obj.id, 'msg': '添加成功!'}
        except Exception as e:
            res = {'code': 500, 'msg': '添加失败%s' % e}

        return JsonResponse(res)

"""
# 列表转字符串，int元素要转str
envs_raw = ",".join(str(x) for x in envs_raw)
envs_raw =  ','.join(list(map(str, envs_raw)))
"""


# ******
def handle_notify_test(request):
    """
    测试通知
    """
    data = json.loads(request.body)
    notify_id = data.get('id')

    notify_row = Notify.objects.get(id=notify_id)
    if not notify_row:
        raise DataNotFoundAppException()

    data = notify_service.notify_user_about_some_event(notify_row)

    res = {'code': 200, 'data': data, 'msg': '测试成功！'}
    return JsonResponse(res)


# ******
@def_operation_log_decorator(
    model=Notify.objects,
    operation_type_id=OperationEnum.UPDATE,
    primary_key='id',
    method='body'
)
def update_notify_status(request):
    """
    更新通知状态
    """
    data = json.loads(request.body)

    current_user_id = data.get('user_id')
    notify_id = data.get('id')
    status = data.get('status')

    Notify.objects.filter(id=notify_id, user__id=current_user_id).update(status=status)
    notify_row = Notify.objects.get(id=notify_id)

    if notify_row.status:
        res = {'code': 200, 'id': notify_id, 'msg': '已启用配置！'}
    else:
        res = {'code': 201, 'id': notify_id, 'msg': '已停用配置！'}

    return JsonResponse(res)


# ******
def notify_echart(request):
    """
    监控统计
    """
    mail_data = Notify.objects.filter(notify_choice=1).count()
    wx_data = Notify.objects.filter(notify_choice=2).count()
    dt_data = Notify.objects.filter(notify_choice=3).count()

    data = {
        'mail_data': mail_data,
        'wx_data': wx_data,
        'dt_data': dt_data,
    }

    res = {'data': data, 'code': 200, 'msg': '成功'}
    return JsonResponse(res)
