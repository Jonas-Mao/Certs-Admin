# -*- coding: utf-8 -*-

from certs_admin.enums.deploy_status_enum import DeployStatusEnum
from certs_admin.enums.ssl_deploy_type_enum import SSLDeployTypeEnum
from certs_admin.enums.status_enum import StatusEnum
from certs_admin.enums.ssl_type_enum import SSLTypeEnum
from django.db import models
from envs.views import Envs
from hosts.models import Host
from django.contrib.auth import get_user_model
User = get_user_model()


class Certs(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="用户")
    envs = models.ForeignKey(Envs, on_delete=models.PROTECT, verbose_name="分组")
    domain = models.CharField(max_length=30, unique=True, verbose_name="域名名称")
    ips_count = models.IntegerField(null=True, default=0, verbose_name="主机数量")
    root_domain = models.CharField(blank=True, null=True, max_length=30, verbose_name="顶级域名")
    port = models.IntegerField(default=443, verbose_name="端口")
    status = models.CharField(max_length=10, default='unverified', choices=(('verified', '已验证'), ('unverified', '未验证')), verbose_name="连接状态")
    issue_time = models.DateTimeField(blank=True, null=True, verbose_name="签发时间")
    expire_time = models.DateTimeField(blank=True, null=True, verbose_name="过期时间")
    remaining_days = models.IntegerField(null=True, default=0, verbose_name="剩余天数")
    total_days = models.IntegerField(null=True, default=0, verbose_name="总共天数")
    is_monitor = models.IntegerField(default=StatusEnum.Enabled, verbose_name="是否监测")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now_add=True, verbose_name="更新时间")
    ssl_type = models.IntegerField(default=SSLTypeEnum.SSL_TLS, verbose_name="加密方式")
    auto_update = models.IntegerField(default=StatusEnum.Enabled, verbose_name="自动更新")
    comment = models.TextField(blank=True, null=True, verbose_name="备注")

    class Meta:
        db_table = "tb_certs"
        verbose_name_plural = "域名证书"
        ordering = ('-id',)


class CertTrusteeship(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="用户")
    envs = models.ForeignKey(Envs, on_delete=models.PROTECT, verbose_name="分组")
    domain = models.CharField(max_length=30, unique=True, verbose_name="域名名称")
    ssl_cert = models.TextField(default=None, null=True, verbose_name="SSL证书")
    ssl_cert_key = models.TextField(default=None, null=True, verbose_name="SSL证书私钥")
    ssl_start_time = models.DateTimeField(default=None, null=True, verbose_name="SSL签发时间")
    ssl_expire_time = models.DateTimeField(default=None, null=True, verbose_name="SSL过期时间")
    remaining_days = models.IntegerField(null=True, default=0, verbose_name="剩余天数")
    total_days = models.IntegerField(null=True, default=0, verbose_name="总共天数")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now_add=True, verbose_name="更新时间")
    comment = models.TextField(blank=True, null=True, verbose_name="备注")

    class Meta:
        db_table = "tb_cert_trusteeship"
        verbose_name_plural = "托管证书"
        ordering = ('-id',)


class CertTrusteeshipDeploy(models.Model):
    cert_trusteeship = models.ForeignKey(CertTrusteeship, on_delete=models.PROTECT, verbose_name="托管证书", related_name="cert_trusteeship_row")
    host = models.ForeignKey(Host, on_delete=models.PROTECT, verbose_name="部署主机")
    deploy_type_id = models.IntegerField(default=SSLDeployTypeEnum.SSH, null=True, verbose_name="部署方式")
    deploy_key_file = models.CharField(default=None, null=True, max_length=50, verbose_name="key部署路径")
    deploy_fullchain_file = models.CharField(default=None, null=True, max_length=50, verbose_name="pem部署路径")
    deploy_reloadcmd = models.CharField(default=None, null=True, max_length=50, verbose_name="重启命令")
    status = models.IntegerField(default=DeployStatusEnum.PENDING, null=True, verbose_name="部署状态")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now_add=True, verbose_name="更新时间")

    class Meta:
        db_table = "tb_cert_trusteeship_deploy"
        verbose_name_plural = "托管证书部署"
        ordering = ('-id',)
