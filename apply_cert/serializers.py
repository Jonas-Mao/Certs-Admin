# -*- coding: utf-8 -*-

from rest_framework import serializers
from apply_cert.models import ApplyCert
from auth_user.serializers import UserSerializer


class ApplyCertsSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)

    class Meta:
        model = ApplyCert
        fields = "__all__"
        read_only_fields = ("id",)