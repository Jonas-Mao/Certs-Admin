# -*- coding: utf-8 -*-

from loggers.models import AsyncTask, LogMonitor, LogOperation, LogScheduler
from rest_framework import serializers
from auth_user.serializers import UserSerializer
from envs.serializers import EnvsSerializer


class AsyncTaskSerializer(serializers.ModelSerializer):

    envs = EnvsSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = AsyncTask
        fields = "__all__"
        read_only_fields = ("id",)


class LogMonitorSerializer(serializers.ModelSerializer):

    class Meta:
        model = LogMonitor
        fields = "__all__"
        read_only_fields = ("id",)


class LogOperationSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)

    class Meta:
        model = LogOperation
        fields = "__all__"
        read_only_fields = ("id",)


class LogSchedulerSerializer(serializers.ModelSerializer):

    class Meta:
        model = LogScheduler
        fields = "__all__"
        read_only_fields = ("id",)