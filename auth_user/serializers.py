# -*- coding: utf-8 -*-

from rest_framework import serializers
from certs.models import Certs
from django.contrib.auth import get_user_model
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    用户序列化器
    """
    class Meta:
        model = User
        fields = "__all__"
        read_only_fields = ("id",)

    """
    证书数量
    """
    certs_count = serializers.SerializerMethodField()

    def get_certs_count(self, obj):
        """
        证书数量
        """
        cert_rows = Certs.objects.filter(user__id=obj.id)
        lst = [row for row in cert_rows]
        return len(lst)