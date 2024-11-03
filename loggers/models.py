# -*- coding: utf-8 -*-

from django.db import models
from certs_admin.enums.monitor_type_enum import MonitorTypeEnum
from certs_admin.enums.monitor_status_enum import MonitorStatusEnum
from certs_admin.enums.operation_enum import OperationEnum
from envs.models import Envs
from django.contrib.auth import get_user_model
User = get_user_model()


class AsyncTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="用户")
    envs = models.ForeignKey(Envs, on_delete=models.PROTECT, verbose_name="分组")
    task_name = models.TextField(default=None, null=True, verbose_name="任务名称")
    function_name = models.CharField(default=None, null=True, max_length=50, unique=True, verbose_name="函数名")
    status = models.BooleanField(default=None, null=True, verbose_name="执行状态")  # None 未执行; True 执行成功; False 执行失败
    result = models.TextField(default=None, null=True, verbose_name="执行结果")
    start_time = models.DateTimeField(default=None, null=True, verbose_name="开始时间")
    end_time = models.DateTimeField(default=None, null=True, verbose_name="结束时间")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now_add=True, verbose_name="更新时间")

    class Meta:
        db_table = "tb_log_async_task"
        verbose_name_plural = "异步任务执行情况记录"
        ordering = ('-id',)


class LogMonitor(models.Model):
    monitor_id = models.IntegerField(default=0, verbose_name="监控ID")
    monitor_type = models.IntegerField(default=MonitorTypeEnum.UNKNOWN, verbose_name="监控类型")
    status = models.IntegerField(default=MonitorStatusEnum.UNKNOWN, verbose_name="状态")
    result = models.TextField(default=None, null=True, verbose_name="结果")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "tb_log_monitor"
        verbose_name_plural = "监控日志"
        ordering = ('-id',)


class LogOperation(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="用户")
    table = models.CharField(default=None, null=True, max_length=30, verbose_name="操作表")
    type_id = models.IntegerField(default=0, verbose_name="操作类型ID")
    before = models.TextField(default=None, null=True, verbose_name="操作之前")
    after = models.TextField(default=None, null=True, verbose_name="操作之后")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "tb_log_operation"
        verbose_name_plural = "操作日志"
        ordering = ('-id',)

    @property
    def type_label(self):
        return OperationEnum.get_label(self.type_id)


class LogScheduler(models.Model):
    status = models.BooleanField(default=False, verbose_name="状态")
    error_message = models.TextField(default=None, null=True, verbose_name="执行结果")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "tb_log_scheduler"
        verbose_name_plural = "定时任务日志"
        ordering = ('-id',)
