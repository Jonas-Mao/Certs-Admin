# -*- coding: utf-8 -*-

from rest_framework import serializers
from certs.models import Certs, CertTrusteeship, CertTrusteeshipDeploy
from auth_user.serializers import UserSerializer
from envs.serializers import EnvsSerializer
from hosts.serializers import HostsSerializer


class CertsSerializer(serializers.ModelSerializer):
    """
    证书序列化器
    """
    envs = EnvsSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Certs
        fields = "__all__"
        read_only_fields = ("id",)


class CertTrusteeshipSerializer(serializers.ModelSerializer):
    """
    托管证书序列化器
    """
    envs = EnvsSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    """
    部署数量
    """
    deploy_count = serializers.SerializerMethodField()
    deploy_success_count = serializers.SerializerMethodField()
    deploy_pending_count = serializers.SerializerMethodField()
    deploy_error_count = serializers.SerializerMethodField()

    def get_deploy_count(self, obj):
        """
        部署总数
        """
        cert_deploy_rows = CertTrusteeshipDeploy.objects.filter(cert_trusteeship__id=obj.id)
        lst = [row for row in cert_deploy_rows]
        return len(lst)

    def get_deploy_success_count(self, obj):
        """
        部署成功
        """
        cert_deploy_rows = CertTrusteeshipDeploy.objects.filter(cert_trusteeship__id=obj.id)
        lst = [row for row in cert_deploy_rows if row.status == 1]
        return len(lst)

    def get_deploy_pending_count(self, obj):
        """
        等待部署
        """
        cert_deploy_rows = CertTrusteeshipDeploy.objects.filter(cert_trusteeship__id=obj.id)
        lst = [row for row in cert_deploy_rows if row.status == 0]
        return len(lst)

    def get_deploy_error_count(self, obj):
        """
        部署失败
        """
        cert_deploy_rows = CertTrusteeshipDeploy.objects.filter(cert_trusteeship__id=obj.id)
        lst = [row for row in cert_deploy_rows if row.status == 2]
        return len(lst)

    class Meta:
        model = CertTrusteeship
        fields = "__all__"
        read_only_fields = ("id",)


class CertTrusteeshipDeploySerializer(serializers.ModelSerializer):
    """
    托管证书部署序列化器
    """
    cert_trusteeship = CertTrusteeshipSerializer(read_only=True)
    host = HostsSerializer(read_only=True)

    class Meta:
        model = CertTrusteeshipDeploy
        fields = "__all__"
        read_only_fields = ("id",)
