# -*- coding: utf-8 -*-

import json
import re
from datetime import datetime
from django.http import JsonResponse
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from certs_admin.enums.operation_enum import OperationEnum
from certs_admin.service.operation_service import class_operation_log_decorator, def_operation_log_decorator
from certs_admin.utils import datetime_util
from certs_admin.utils.django_ext.app_exception import DataNotFoundAppException
from certs_admin.enums.method_type_enum import MethodTypeEnum
from certs_admin.enums.monitor_type_enum import MonitorTypeEnum
from certs_admin.enums.operation_enum import OperationEnum
from certs_admin.service import monitor_service, auth_service
from certs_apscheduler.scheduler_service import scheduler_main, scheduler_config, scheduler_log, scheduler_util
from rest_framework.viewsets import ModelViewSet
from rest_framework import filters
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from monitor.models import Monitor
from envs.models import Envs
from monitor.serializers import MonitorSerializer
from django.contrib.auth import get_user_model
User = get_user_model()


class MonitorViewSet(ModelViewSet):
    queryset = Monitor.objects.all()
    serializer_class = MonitorSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ('title',)
    filter_fields = ('title',)

    # @auth_service.permission(role=RoleEnum.USER)
    @method_decorator(class_operation_log_decorator(
        model=Monitor.objects,
        operation_type_id=OperationEnum.UPDATE,
        primary_key='id')
    )
    def update(self, request, pk=None, *args, **kwargs):
        """
        更新监测
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            error = json.dumps(e.detail, ensure_ascii=False)
            error = re.sub(r'[\[\]{}"\s]', '', error)   # 替换[]、{}、"和空格
            res = {'code': e.status_code, 'msg': error}
            return Response(res)
        self.perform_update(serializer)

        scheduler_main.run_one_monitor_task(Monitor.objects.get(id=pk))

        res = {'code': 200, 'id': pk, 'msg': '更新成功！'}
        return JsonResponse(res)

    # @auth_service.permission(role=RoleEnum.USER)
    @method_decorator(class_operation_log_decorator(
        model=Monitor.objects,
        operation_type_id=OperationEnum.DELETE,
        primary_key='pk')
    )
    def destroy(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        res = {'code': 200, 'msg': '删除成功！'}
        return JsonResponse(res)

    @method_decorator(class_operation_log_decorator(
        model=Monitor.objects,
        operation_type_id=OperationEnum.CREATE,
        primary_key='id')
    )
    def create(self, request, *args, **kwargs):
        """
        添加监测
        """
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            error = json.dumps(e.detail, ensure_ascii=False)
            error = re.sub(r'[\[\]{}"\s]', '', error)  # 替换[]、{}、"和空格
            res = {'code': e.status_code, 'msg': error}
            return Response(res)

        title = request.data.get('title')
        monitor_type = request.data.get('monitor_type') or MonitorTypeEnum.HTTP
        method = request.data.get('method') or MethodTypeEnum.GET
        url = request.data.get('url')
        timeout = request.data.get('timeout')
        interval = request.data.get('interval')
        retries = request.data.get('retries')

        monitor_queryset = Monitor.objects.filter(title=title)
        if monitor_queryset:
            res = {'code': 500, 'msg': '%s已存在！' % title}
            return Response(res)

        monitor_obj = Monitor.objects.create(
            title=title,
            url=url,
            monitor_type=monitor_type,
            method=method,
            timeout=timeout,
            interval=interval,
            retries=retries,
            user=User.objects.get(id=request.user.id),
            envs=Envs.objects.get(id=request.data.get('envs'))
        )

        scheduler_main.run_one_monitor_task(Monitor.objects.get(id=monitor_obj.id))

        res = {'code': 200, 'id': monitor_obj.id,'msg': '创建成功！'}
        return JsonResponse(res)

    def perform_update(self, serializer):
        user = User.objects.get(id=self.request.data.get('user'))
        envs = Envs.objects.get(id=self.request.data.get('envs'))
        update_time = datetime_util.get_datetime()
        serializer.save(
            user=user,
            envs=envs,
            update_time=update_time
        )


# ******
@def_operation_log_decorator(
    model=Monitor.objects,
    operation_type_id=OperationEnum.UPDATE,
    primary_key='id',
    method='body'
)
def update_monitor_active(request):
    """
    监测按钮
    """
    data = json.loads(request.body)
    monitor_id = data.get('id')
    is_active = data.get('is_active')
    current_user_id = data.get('user_id') or 1
    next_run_time = datetime.now() if is_active else None

    monitor_row = Monitor.objects.get(id=monitor_id, user__id=current_user_id)
    if not monitor_row:
        raise DataNotFoundAppException()

    Monitor.objects.filter(id=monitor_row.id).update(
        is_active=is_active,
        next_run_time=next_run_time
    )
    if is_active:
        scheduler_main.run_one_monitor_task(Monitor.objects.get(id=monitor_id))
        res = {'code': 200, 'id': monitor_id, 'msg': '已开启监测！'}
    else:
        res = {'code': 201, 'id': monitor_id, 'msg': '已关闭监测！'}

    return JsonResponse(res)


# ******
def monitor_abnormality_count(request):
    """
    过期证书数量
    """
    abnormality_count = Monitor.objects.exclude(status=1).count()

    res = {'code': 200, 'count': abnormality_count}
    return JsonResponse(res)


# ******
def monitor_echart(request):
    """
    Dashboard统计
    """
    abnormality_data = Monitor.objects.filter(status=2).count()
    unknown_data = Monitor.objects.filter(status=0).count()
    normality_data = Monitor.objects.filter(status=1).count()

    data = {
        'abnormality_data': abnormality_data,
        'unknown_data': unknown_data,
        'normality_data': normality_data,
    }

    res = {'data': data, 'code': 200, 'msg': '成功'}
    return JsonResponse(res)
