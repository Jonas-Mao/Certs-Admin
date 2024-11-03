# -*- coding: utf-8 -*-

from certs_admin.utils import datetime_util
from dnss.models import Dns
from rest_framework import serializers
from auth_user.serializers import UserSerializer


class DnsSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)

    class Meta:
        model = Dns
        fields = "__all__"
        read_only_fields = ("id",)

    def update(self, instance, validated_data):
        instance.dns_type = validated_data.get('dns_type')
        instance.name = validated_data.get('name')
        instance.access_key = validated_data.get('access_key')
        instance.secret_key = validated_data.get('secret_key')
        instance.comment = validated_data.get('comment')
        instance.update_time = datetime_util.get_datetime()
        instance.save()
        return instance


"""
class DomainIcpSerializer(serializers.ModelSerializer):

    class Meta:
        model = DomainIcp
        fields = "__all__"
        read_only_fields = ("id",)
"""