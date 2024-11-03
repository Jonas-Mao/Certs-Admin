# -*- coding: utf-8 -*-

from certs_admin.config.default_config import DEFAULT_SSH_PORT
from certs_admin.enums.host_auth_type_enum import HostAuthTypeEnum
from django.db import models
from envs.models import Envs
from django.contrib.auth import get_user_model
User = get_user_model()


class Host(models.Model):
    host = models.CharField(default=None, null=True, max_length=30, unique=True, verbose_name="远程主机")
    port = models.IntegerField(default=DEFAULT_SSH_PORT, null=True, verbose_name="远程端口")
    username = models.CharField(default=None, null=True, max_length=30, verbose_name="远程用户")
    auth_type = models.IntegerField(default=HostAuthTypeEnum.PASSWORD, verbose_name="验证方式")
    password = models.TextField(blank=True, null=True, verbose_name="密码")
    private_key = models.TextField(blank=True, null=True, verbose_name="密钥")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now_add=True, verbose_name="更新时间")
    comment = models.TextField(blank=True, null=True, verbose_name="备注")

    class Meta:
        db_table = "tb_host"
        verbose_name_plural = "证书部署主机"
        ordering = ('-id',)
