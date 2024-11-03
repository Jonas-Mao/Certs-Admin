# -*- coding: utf-8 -*-

from system.models import System
from rest_framework import serializers


class SystemSerializer(serializers.ModelSerializer):

    class Meta:
        model = System
        fields = "__all__"
        read_only_fields = ("id",)
