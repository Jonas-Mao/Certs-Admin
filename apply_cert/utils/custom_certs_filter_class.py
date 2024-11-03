# -*- coding: utf-8 -*-

import django_filters
from django_filters.rest_framework import FilterSet
from apply_cert.models import ApplyCert


class ApplyCertFilter(FilterSet):
    """
    Apply_Cert 过滤器类，模糊查询
    """
    domains = django_filters.CharFilter(field_name='domains', lookup_expr='icontains')    # icontains，包含且忽略大小写

    class Meta:
        models = ApplyCert
        fields = ['domains']
