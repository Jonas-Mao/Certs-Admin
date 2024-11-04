# -*- coding: utf-8 -*-

import json
import re
from django.utils.decorators import method_decorator
from certs_admin.enums.operation_enum import OperationEnum
from certs_admin.service.operation_service import class_operation_log_decorator, def_operation_log_decorator
from certs_admin.utils import datetime_util
from hosts.utils.crypto_pass import encrypt_pass, decrypt_pass
from django_filters.rest_framework import DjangoFilterBackend
from django.http import JsonResponse
from rest_framework.viewsets import ModelViewSet
from rest_framework import filters
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from hosts.serializers import HostsSerializer
from hosts.models import Host
from django.contrib.auth import get_user_model
User = get_user_model()


class HostViewSet(ModelViewSet):
    queryset = Host.objects.all()
    serializer_class = HostsSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]  # 指定过滤器
    search_fields = ('host',)
    filterset_fields = ('host',)

    def get_permissions(self):
        if self.action == 'list':
            return [permissions.IsAuthenticated()]
        if self.action == 'retrieve':
            return [permissions.IsAuthenticated()]
        if self.action == 'create':
            return [permissions.IsAdminUser()]
        if self.action == 'update':
            return [permissions.IsAdminUser()]
        if self.action == 'destroy':
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    @method_decorator(class_operation_log_decorator(
        model=Host.objects,
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

    @method_decorator(class_operation_log_decorator(
        model=Host.objects,
        operation_type_id=OperationEnum.DELETE,
        primary_key='pk')
    )
    def destroy(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        res = {'code': 200, 'msg': '删除成功！'}
        return JsonResponse(res)

    @method_decorator(class_operation_log_decorator(
        model=Host.objects,
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

    def perform_create(self, serializer):
        auth_type = self.request.data.get('auth_type')
        if auth_type == 0:
            password = encrypt_pass(
                self.request.data.get('password'),
                self.request.data.get('host')
            )
            serializer.save(password=password)
        else:
            private_key = encrypt_pass(
                self.request.data.get('private_key'),
                self.request.data.get('host')
            )
            serializer.save(private_key=private_key)

    def perform_update(self, serializer):
        update_time = datetime_util.get_datetime()
        auth_type = self.request.data.get('auth_type')
        if auth_type == 0:
            password = encrypt_pass(
                self.request.data.get('password'),
                self.request.data.get('host')
            )
            serializer.save(password=password, update_time=update_time)
        else:
            private_key = encrypt_pass(
                self.request.data.get('private_key'),
                self.request.data.get('host')
            )
            serializer.save(private_key=private_key, update_time=update_time)
