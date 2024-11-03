# -*- coding: utf-8 -*-

import json
from django.db import models
from certs_admin.enums.event_enum import EventEnum
from certs_admin.enums.notify_type_enum import NotifyTypeEnum
from certs_admin.config.default_config import DEFAULT_BEFORE_EXPIRE_DAYS
from certs_admin.enums.status_enum import StatusEnum
from envs.models import Envs
from django.contrib.auth import get_user_model
User = get_user_model()


class Notify(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="用户")
    envs = models.ManyToManyField(Envs, verbose_name="分组")        # 多对多
    title = models.CharField(max_length=100, unique=True, verbose_name="名称")
    event_id = (
        (1, "SSL证书到期"),
        (2, "托管证书到期"),
        (3, "网站监控系统"),
        (4, "监控异常恢复")
    )
    event_id = models.IntegerField(choices=event_id, default=EventEnum.SSL_CERT_EXPIRE, verbose_name="事件类型")
    expire_days = models.IntegerField(default=DEFAULT_BEFORE_EXPIRE_DAYS, verbose_name="过期剩余天数")
    value_raw = models.TextField(default=None, null=True, verbose_name="原始值")
    notify_choice = (
        (1, "Email"),
        (2, "WeChat"),
        (3, "DingTalk"),
        (4, "WebHook")
    )
    notify_choice = models.IntegerField(choices=notify_choice, default=NotifyTypeEnum.Email, verbose_name="通知方式")
    status = models.IntegerField(null=False, default=StatusEnum.Enabled, verbose_name="启用状态")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now_add=True, verbose_name="更新时间")

    class Meta:
        db_table = "tb_notify"
        verbose_name_plural = "通知配置"
        ordering = ('-id',)


    @property
    def value(self):
        if self.value_raw:
            return json.loads(self.value_raw)
        else:
            return None

    # email参数
    @property
    def email_list(self):
        if self.value:
            return self.value.get('email_list')

    # webhook参数
    @property
    def webhook_method(self):
        if self.value:
            return self.value.get('method')

    @property
    def webhook_url(self):
        if self.value:
            return self.value.get('url')

    @property
    def webhook_headers(self):
        if self.value:
            return self.value.get('headers')

    @property
    def webhook_body(self):
        if self.value:
            return self.value.get('body')

    # 微信参数
    @property
    def weixin_corpid(self):
        if self.value:
            return self.value.get('corpid')

    @property
    def weixin_corpsecret(self):
        if self.value:
            return self.value.get('corpsecret')

    @property
    def weixin_body(self):
        if self.value:
            return self.value.get('body')

    # dingtalk
    @property
    def dingtalk_appkey(self):
        if self.value:
            return self.value.get('appkey')

    @property
    def dingtalk_appsecret(self):
        if self.value:
            return self.value.get('appsecret')

    @property
    def dingtalk_body(self):
        if self.value:
            return self.value.get('body')

    # 飞书
    @property
    def feishu_body(self):
        if self.value:
            return self.value.get('body')

    @property
    def feishu_params(self):
        if self.value:
            return self.value.get('params')

    @property
    def feishu_app_id(self):
        if self.value:
            return self.value.get('app_id')

    @property
    def feishu_app_secret(self):
        if self.value:
            return self.value.get('app_secret')
