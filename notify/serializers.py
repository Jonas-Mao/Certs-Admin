# -*- coding: utf-8 -*-

from notify.models import Notify
from rest_framework import serializers
from auth_user.serializers import UserSerializer
from envs.serializers import EnvsSerializer


class NotifySerializer(serializers.ModelSerializer):

    envs = EnvsSerializer(many=True, read_only=True)  # 多对多
    user = UserSerializer(read_only=True)

    class Meta:
        model = Notify
        fields = "__all__"
        read_only_fields = ("id",)