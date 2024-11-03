# -*- coding: utf-8 -*-

from monitor.models import Monitor
from rest_framework import serializers
from auth_user.serializers import UserSerializer
from envs.serializers import EnvsSerializer


class MonitorSerializer(serializers.ModelSerializer):

    envs = EnvsSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Monitor
        fields = "__all__"
        read_only_fields = ("id",)