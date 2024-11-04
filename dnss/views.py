# -*- coding: utf-8 -*-

import json
import re
from django_filters.rest_framework import DjangoFilterBackend
from django.http import JsonResponse
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ModelViewSet
from rest_framework import filters
from rest_framework import permissions
from rest_framework.response import Response
from certs_admin.service import issue_cert_service, auth_service
from certs_admin.enums.role_enum import RoleEnum
from certs_admin.enums.challenge_deploy_type_enum import ChallengeDeployTypeEnum
from certs_admin.enums.deploy_status_enum import DeployStatusEnum
from certs_admin.utils.django_ext.app_exception import DataNotFoundAppException
from certs_admin.utils import datetime_util
from dnss.serializers import DnsSerializer
from dnss.models import Dns
from apply_cert.models import ApplyCert
from django.contrib.auth import get_user_model
User = get_user_model()


class DnsViewSet(ModelViewSet):
    queryset = Dns.objects.all()
    serializer_class = DnsSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]  # 指定过滤器
    search_fields = ('name',)
    filter_fields = ('name',)

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

    def update(self, request, pk=None, *args, **kwargs):
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
            error = re.sub(r'[\[\]{}"\s]', '', error)   # 替换[]、{}、"和空格
            res = {'code': e.status_code, 'msg': error}
            return Response(res)
        self.perform_create(serializer)

        res = {'code': 200, 'msg': '添加成功！'}
        return Response(res)

    def perform_update(self, serializer):
        update_time = datetime_util.get_datetime()
        serializer.save(update_time=update_time)


# ******
@auth_service.permission(role=RoleEnum.USER)
def add_dns_domain_record(request):
    """
    添加dns记录
    """
    data = json.loads(request.body)

    current_user_id = data.get('user') or 1
    issue_cert_id = data.get('issue_cert_id')
    dns_id = data.get('dns_id')

    issue_cert_row = ApplyCert.objects.filter(
        id=issue_cert_id,
        user__id=current_user_id
    )
    if not issue_cert_row:
        raise DataNotFoundAppException()

    # 添加txt记录
    issue_cert_service.add_dns_domain_record(
        dns_id=dns_id,
        issue_cert_id=issue_cert_id
    )

    # 更新验证信息
    ApplyCert.objects.filter(id=issue_cert_id).update(
        challenge_deploy_type_id=ChallengeDeployTypeEnum.DNS,
        challenge_deploy_dns_id=dns_id,
        challenge_deploy_status=DeployStatusEnum.SUCCESS
    )

    res = {'code': 200, 'msg': '添加成功！'}
    return JsonResponse(res)
