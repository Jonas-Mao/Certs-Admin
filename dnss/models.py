# -*- coding: utf-8 -*-

from django.db import models
from certs_admin.enums.dns_type_enum import DnsTypeEnum
from django.contrib.auth import get_user_model
User = get_user_model()


class Dns(models.Model):
    dns_type = models.IntegerField(default=DnsTypeEnum.ALIYUN, verbose_name="DNS类型")
    name = models.CharField(max_length=50, verbose_name="名称")
    access_id = models.CharField(default=None, max_length=100, verbose_name="Access ID")
    access_secret = models.CharField(default=None, max_length=100, verbose_name="Access Secret")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now_add=True, verbose_name="更新时间")
    comment = models.TextField(blank=True, null=True, verbose_name="备注")

    class Meta:
        db_table = "tb_dns"
        verbose_name_plural = "DNS账号"
        ordering = ('-id',)
