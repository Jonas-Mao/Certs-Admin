# -*- coding: utf-8 -*-

import re
import json
from loggers.models import AsyncTask, LogMonitor, LogOperation, LogScheduler
from loggers.serializers import AsyncTaskSerializer, LogMonitorSerializer, LogOperationSerializer, LogSchedulerSerializer
from django_filters.rest_framework import DjangoFilterBackend
from django.http import JsonResponse
from django.forms import model_to_dict
from rest_framework.viewsets import ModelViewSet
from rest_framework import filters
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from certs_admin.utils import datetime_util
from envs.models import Envs
from django.contrib.auth import get_user_model
User = get_user_model()

from certs_admin.enums.role_enum import RoleEnum
from certs_admin.service import auth_service


class AsyncTaskViewSet(ModelViewSet):
    queryset = AsyncTask.objects.all()
    serializer_class = AsyncTaskSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]  # 指定过滤器
    search_fields = ('task_name',)
    filter_fields = ('task_name',)

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

        res = {'code': 200, 'msg': '更新成功！'}
        return Response(res)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        res = {'code': 200, 'msg': '删除成功！'}
        return Response(res)

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

        res = {'code': 200, 'msg': '添加成功！'}
        return Response(res)

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


#
def clear_all_log_asynctask(request):
    AsyncTask.objects.all().delete()
    return JsonResponse({'code': 200, 'msg': '清空成功！'})


class LogMonitorViewSet(ModelViewSet):
    queryset = LogMonitor.objects.all()
    serializer_class = LogMonitorSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]  # 指定过滤器
    search_fields = ('monitor_type',)
    filter_fields = ('monitor_type',)

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

        res = {'code': 200, 'msg': '更新成功！'}
        return Response(res)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        res = {'code': 200, 'msg': '删除成功！'}
        return Response(res)

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

        res = {'code': 200, 'msg': '添加成功！'}
        return Response(res)

    def perform_update(self, serializer):
        update_time = datetime_util.get_datetime()
        serializer.save(update_time=update_time)


#
def clear_all_log_monitor(request):
    LogMonitor.objects.all().delete()
    return JsonResponse({'code': 200, 'msg': '清空成功！'})


class LogOperationViewSet(ModelViewSet):
    queryset = LogOperation.objects.all()
    serializer_class = LogOperationSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]  # 指定过滤器
    search_fields = ('table',)
    filter_fields = ('table',)

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

        res = {'code': 200, 'msg': '更新成功！'}
        return Response(res)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        res = {'code': 200, 'msg': '删除成功！'}
        return Response(res)

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

        res = {'code': 200, 'msg': '添加成功！'}
        return Response(res)

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


#
def clear_all_log_operationt(request):
    LogOperation.objects.all().delete()
    return JsonResponse({'code': 200, 'msg': '清空成功！'})


class LogSchedulerViewSet(ModelViewSet):
    queryset = LogScheduler.objects.all()
    serializer_class = LogSchedulerSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]  # 指定过滤器
    search_fields = ('status',)
    filter_fields = ('status',)

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

        res = {'code': 200, 'msg': '更新成功！'}
        return Response(res)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        res = {'code': 200, 'msg': '删除成功！'}
        return Response(res)

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

        res = {'code': 200, 'msg': '添加成功！'}
        return Response(res)

    def perform_update(self, serializer):
        update_time = datetime_util.get_datetime()
        serializer.save(update_time=update_time)


#
def clear_all_log_scheduler(request):
    LogScheduler.objects.all().delete()
    return JsonResponse({'code': 200, 'msg': '清空成功！'})


'''
def get_operation_log_list(request):
    """
    获取操作日志列表
    """
    query = LogOperation.objects
    total = query.count()
    lst = []

    if total > 0:
        rows = query.all().order_by('-create_time', '-id')

        lst = [model_to_dict(
            row,
            fields=[
                'user',
                'table',
                'type_id',
                'before',
                'after',
                'create_time'
            ]
        ) for row in rows]

    return JsonResponse(
        {
            'code': 200,
            'list': lst,
            'msg': '获取成功！'
        }
    )
'''