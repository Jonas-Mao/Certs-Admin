# -*- coding: utf-8 -*-

from rest_framework import serializers
from hosts.models import Host


class HostsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Host
        fields = "__all__"
        read_only_fields = ("id",)
