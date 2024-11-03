# -*- coding: utf-8 -*-

import json
from django.db import models
from certs_admin.utils.acme_util.cert_provider_type_enum import CertProviderTypeEnum
from certs_admin.utils.acme_util.key_type_enum import KeyTypeEnum
from certs_admin.utils.acme_util.challenge_type import ChallengeType
from certs_admin.enums.challenge_deploy_type_enum import ChallengeDeployTypeEnum
from certs_admin.enums.deploy_status_enum import DeployStatusEnum
from certs_admin.enums.valid_status_enum import ValidStatus
from certs_admin.enums.status_enum import StatusEnum
from certs_admin.enums.ssl_deploy_type_enum import SSLDeployTypeEnum
from envs.models import Envs
from django.contrib.auth import get_user_model

User = get_user_model()


class ApplyCert(models.Model):
    """
    申请证书
    1、验证域名
    2、签发证书
    3、部署证书
    """
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="用户")
    domains = models.CharField(unique=True, max_length=50, verbose_name="域名列表")
    ssl_cert = models.TextField(default=None, null=True, verbose_name="SSL证书")
    ssl_cert_key = models.TextField(default=None, null=True, verbose_name="SSL证书私钥")
    ssl_start_time = models.DateTimeField(default=None, null=True, verbose_name="SSL签发时间")
    ssl_expire_time = models.DateTimeField(default=None, null=True, verbose_name="SSL过期时间")
    directory_type = models.CharField(default=CertProviderTypeEnum.LETS_ENCRYPT, null=True, max_length=30, verbose_name="证书提供商")
    key_type = models.CharField(default=KeyTypeEnum.RSA, null=True, max_length=30, verbose_name="加密方式")
    challenge_type = models.CharField(default=ChallengeType.HTTP01, null=True, max_length=30, verbose_name="域名验证类型")
    challenge_deploy_type_id = models.IntegerField(default=ChallengeDeployTypeEnum.SSH, verbose_name="验证文件部署方式")
    challenge_deploy_host_id = models.IntegerField(default=0, null=True, verbose_name="验证文件部署主机id")
    challenge_deploy_status = models.IntegerField(default=DeployStatusEnum.PENDING, verbose_name="验证文件部署状态")
    challenge_deploy_verify_path = models.CharField(default=None, null=True, max_length=50, verbose_name="验证文件部署目录")
    token = models.CharField(default=None, null=True, max_length=100, verbose_name="域名验证token")
    validation = models.CharField(default=None, null=True, max_length=100, verbose_name="域名验证数据")
    challenge_deploy_dns_id = models.IntegerField(default=0, null=True, verbose_name="验证dns记录id")
    status = models.CharField(default=ValidStatus.PENDING, null=True, max_length=100, verbose_name="验证状态")
    deploy_type_id = models.IntegerField(default=SSLDeployTypeEnum.SSH, null=True, verbose_name="部署方式")
    deploy_host_id = models.IntegerField(default=0, verbose_name="部署主机")
    deploy_header_raw = models.TextField(default=None, null=True, verbose_name="部署请求头")
    deploy_params_raw = models.TextField(default=None, null=True, verbose_name="部署参数")
    deploy_key_file = models.CharField(default=None, null=True, max_length=50, verbose_name="key部署路径")
    deploy_fullchain_file = models.CharField(default=None, null=True, max_length=50, verbose_name="pem部署路径")
    deploy_reloadcmd = models.CharField(default=None, null=True, max_length=50, verbose_name="部署重启命令")
    deploy_url = models.CharField(default=None, null=True, max_length=100, verbose_name="部署请求url")
    deploy_status = models.IntegerField(default=DeployStatusEnum.PENDING, null=True, verbose_name="证书部署状态")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now_add=True, verbose_name="更新时间")
    is_auto_renew = models.IntegerField(default=StatusEnum.Disabled, verbose_name="自动续期")
    comment = models.TextField(blank=True, null=True, verbose_name="备注")

    class Meta:
        db_table = "tb_apply_certs"
        verbose_name_plural = "申请证书"
        ordering = ('-id',)

    @property
    def can_auto_renew(self):
        """
        能够选择自动续期
        """
        return self.deploy_status == DeployStatusEnum.SUCCESS \
            and self.challenge_deploy_status == DeployStatusEnum.SUCCESS

    '''
    @property
    def domains(self):
        if self.domains:
            return json.loads(self.domains)
        else:
            return []

    @property
    def deploy_header(self):
        if self.deploy_header_raw:
            return json.loads(self.deploy_header_raw)
        else:
            return {}
    '''

