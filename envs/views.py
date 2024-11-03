# -*- coding: utf-8 -*-

import json
import re
from certs_admin.utils import datetime_util
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from certs_admin.enums.operation_enum import OperationEnum
from certs_admin.service.operation_service import class_operation_log_decorator, def_operation_log_decorator
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import filters
from envs.models import Envs
from envs.serializers import EnvsSerializer


class EnvsViewSet(ModelViewSet):
    queryset = Envs.objects.all()
    serializer_class = EnvsSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]  # 指定过滤器
    search_fields = ('name', 'en_name')
    filter_fields = ('name', 'en_name')

    @method_decorator(class_operation_log_decorator(
        model=Envs.objects,
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
        model=Envs.objects,
        operation_type_id=OperationEnum.DELETE,
        primary_key='pk')
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        res = {'code': 200, 'msg': '删除成功！'}
        return JsonResponse(res)

    @method_decorator(class_operation_log_decorator(
        model=Envs.objects,
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

    def perform_update(self, serializer):
        update_time = datetime_util.get_datetime()
        serializer.save(update_time=update_time)
