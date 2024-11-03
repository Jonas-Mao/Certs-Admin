# -*- coding: utf-8 -*-

from certs_admin.utils import datetime_util
from envs.models import Envs
from rest_framework import serializers


class EnvsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Envs
        fields = "__all__"
        read_only_fields = ("id",)

    # def update(self, instance, validated_data):
    #     instance.name = validated_data.get('name')
    #     instance.en_name = validated_data.get('en_name')
    #     instance.comment = validated_data.get('comment')
    #     instance.update_time = datetime_util.get_datetime()
    #     instance.save()
    #     return instance
