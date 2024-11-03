# -*- coding: utf-8 -*-

from django.db import models
from certs_admin.enums.status_enum import StatusEnum
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps
from certs_admin.enums.config_key_enum import ConfigKeyEnum


class System(models.Model):
    key = models.CharField(max_length=50, unique=True, verbose_name="键")
    value = models.CharField(default=None, null=False, max_length=100, verbose_name="值")
    label = models.CharField(default=None, null=True, max_length=50, verbose_name="显示")
    placeholder = models.CharField(max_length=50, verbose_name="输入提示")
    is_show_value = models.IntegerField(default=StatusEnum.Enabled, null=True, verbose_name="对外显示值")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now_add=True, verbose_name="更新时间")

    class Meta:
        db_table = "tb_system"
        verbose_name_plural = "系统配置"
        ordering = ('-id',)


@receiver(post_migrate)
def add_default_envs(sender, **kwargs):
    """
    添加默认数据
    """
    # 确保只在应用初次迁移后执行
    if not apps.ready:
        return

    data = [
        {
            'key': ConfigKeyEnum.MAIL_HOST,
            'value': 'smtp.qq.com',
            'label': '发件邮箱服务器地址',
            'placeholder': '发件邮箱服务器地址',
            'is_show_value': True,
        },
        {
            'key': ConfigKeyEnum.MAIL_PORT,
            'value': 25,
            'label': '发件邮箱服务器端口',
            'placeholder': '发件邮箱服务器端口：25 或者 465(ssl)',
            'is_show_value': True,
        },
        {
            'key': ConfigKeyEnum.MAIL_ALIAS,
            'value': 'Certs Admin',
            'label': '发件人邮箱名称',
            'placeholder': '发件人邮箱名称',
            'is_show_value': True,
        },
        {
            'key': ConfigKeyEnum.MAIL_USERNAME,
            'value': 'ssl_certs@qq.com',
            'label': '发件人邮箱账号',
            'placeholder': '发件人邮箱账号',
            'is_show_value': True,
        },
        {
            'key': ConfigKeyEnum.MAIL_PASSWORD,
            'value': 'ugtraumlocygbgbh',
            'label': '发件人邮箱密码',
            'placeholder': '发件人邮箱密码或客户端授权码',
            'is_show_value': True,
        },
        {
            'key': ConfigKeyEnum.SCHEDULER_CRON,
            'value': '30 10 * * *',
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

    try:
        System.objects.get(key=ConfigKeyEnum.MAIL_HOST)
    except System.DoesNotExist:
        System.objects.bulk_create(objects)
