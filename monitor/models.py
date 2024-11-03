# -*- coding: utf-8 -*-

from django.db import models
from certs_admin.enums.monitor_type_enum import MonitorTypeEnum
from certs_admin.enums.monitor_status_enum import MonitorStatusEnum
from certs_admin.enums.status_enum import StatusEnum
from envs.models import Envs
from django.contrib.auth import get_user_model
User = get_user_model()


class Monitor(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="用户")
    envs = models.ForeignKey(Envs, on_delete=models.PROTECT, verbose_name="分组")
    title = models.CharField(max_length=100, unique=True, verbose_name="监测名称")
    monitor_type = models.IntegerField(default=MonitorTypeEnum.HTTP, verbose_name="监测类型")
    method = models.CharField(max_length=10, default="GET", verbose_name="请求方式")
    url = models.CharField(max_length=100, default=None, verbose_name="请求URL")
    timeout = models.IntegerField(default=3, verbose_name="请求超时")
    interval = models.IntegerField(default=60, verbose_name="检测频率")
    retries = models.IntegerField(default=0, verbose_name="重试次数")
    status = models.IntegerField(default=MonitorStatusEnum.UNKNOWN, verbose_name="状态")
    is_active = models.IntegerField(default=StatusEnum.Enabled, verbose_name="是否监测")
    next_run_time = models.DateTimeField(blank=True, null=True, verbose_name="下次运行时间")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now_add=True, verbose_name="更新时间")

    class Meta:
        db_table = "tb_monitor"
        verbose_name_plural = "监控任务"
        ordering = ('-id',)
