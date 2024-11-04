# -*- coding: utf-8 -*-

import re
import json
import traceback
from certs_admin.utils import datetime_util
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from certs_apscheduler import scheduler_service
from certs_apscheduler.scheduler_service import scheduler_main
from certs_admin.utils import email_util
from rest_framework import permissions
from certs_admin.service import auth_service
from certs_admin.enums.role_enum import RoleEnum
from certs_admin.enums.config_key_enum import ConfigKeyEnum
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ModelViewSet
from rest_framework import filters
from rest_framework.response import Response
from system.models import System
from system.utils.system_log import logger
from system.serializers import SystemSerializer


class SystemViewSet(ModelViewSet):
    queryset = System.objects.all()
    serializer_class = SystemSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]  # 指定过滤器
    search_fields = ('key',)
    filter_fields = ('key',)

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

    def create(self, request, *args, **kwargs):
        """
        首次创建
        """
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            error = json.dumps(e.detail, ensure_ascii=False)
            error = re.sub(r'[\[\]{}"\s]', '', error)   # 替换[]、{}、"和空格
            res = {'code': e.status_code, 'msg': error}
            return Response(res)

        mail_host = request.data.get('mail_host')
        mail_port = request.data.get('mail_port')
        mail_alias = request.data.get('mail_alias')
        mail_username = request.data.get('mail_username')
        mail_password = request.data.get('mail_password')
        scheduler_cron = request.data.get('scheduler_cron')

        data = [
            {
                'key': ConfigKeyEnum.MAIL_HOST,
                'value': mail_host,
                'label': '发件邮箱服务器地址',
                'placeholder': '发件邮箱服务器地址',
                'is_show_value': True,
            },
            {
                'key': ConfigKeyEnum.MAIL_PORT,
                'value': mail_port,
                'label': '发件邮箱服务器端口',
                'placeholder': '发件邮箱服务器端口：25 或者 465(ssl)',
                'is_show_value': True,
            },
            {
                'key': ConfigKeyEnum.MAIL_ALIAS,
                'value': mail_alias,
                'label': '发件人邮箱名称',
                'placeholder': '发件人邮箱名称',
                'is_show_value': True,
            },
            {
                'key': ConfigKeyEnum.MAIL_USERNAME,
                'value': mail_username,
                'label': '发件人邮箱账号',
                'placeholder': '发件人邮箱账号',
                'is_show_value': True,
            },
            {
                'key': ConfigKeyEnum.MAIL_PASSWORD,
                'value': mail_password,
                'label': '发件人邮箱密码',
                'placeholder': '发件人邮箱密码或客户端授权码',
                'is_show_value': True,
            },
            {
                'key': ConfigKeyEnum.SCHEDULER_CRON,
                'value': scheduler_cron,
                'label': '定时检测时间（crontab 表达式）',
                'placeholder': '分 时 日 月 周',
                'is_show_value': True,
            }
        ]

        objects = [
            System(
                key=item['key'],
                value=item['value'],
                is_show_value=item['is_show_value'],
                label=item['label'],
                placeholder=item['placeholder']
            ) for item in data]

        System.objects.bulk_create(objects)


# ******
@auth_service.permission(role=RoleEnum.USER)
def update_mail_conf(request):
    """
    更新邮件设置
    """
    data = json.loads(request.body)
    keys = [
        ConfigKeyEnum.MAIL_HOST,
        ConfigKeyEnum.MAIL_PORT,
        ConfigKeyEnum.MAIL_ALIAS,
        ConfigKeyEnum.MAIL_USERNAME,
        ConfigKeyEnum.MAIL_PASSWORD,
    ]

    for key in keys:
        value = data.get(key)

        System.objects.filter(key=key).update(
            value=value,
            update_time=datetime_util.get_datetime()
        )

    res = {'code': 200, 'msg': '更新成功！'}
    return JsonResponse(res)


# ******
@auth_service.permission(role=RoleEnum.ADMIN)
def update_cron_conf(request):
    """
    更新定时设置
    """
    data = json.loads(request.body)
    scheduler_cron = data.get('scheduler_cron')

    System.objects.filter(key='scheduler_cron').update(
        value=scheduler_cron,
        update_time=datetime_util.get_datetime()
    )

    # 更新定时
    scheduler_service.update_job(scheduler_cron)

    res = {'code': 200, 'msg': '更新成功！'}
    return JsonResponse(res)


# ******
def handle_mail_test(request):
    """
    测试邮件
    """
    data = json.loads(request.body)

    mail_host = data.get('mail_host')
    mail_port = data.get('mail_port')
    mail_alias = data.get('mail_alias')
    mail_username = data.get('mail_username')
    mail_password = data.get('mail_password')

    subject = data.get('subject')
    content = data.get('content')
    receiver = data.get('receiver', None)
    receiver = (receiver,)

    try:
        email_util.send_email(
            subject=subject,
            content=content,
            to_addresses=receiver,
            mail_host=mail_host,
            mail_port=mail_port,
            content_type='plain',
            mail_alias=mail_alias,
            mail_username=mail_username,
            mail_password=mail_password
        )
    except:
        logger.error(traceback.format_exc())

    res = {'code': 200, 'msg': '发送成功！'}
    return JsonResponse(res)


# ******
def get_monitor_task_next_run_time():
    return {
        'next_run_time': scheduler_main.get_monitor_task_next_run_time()
    }
