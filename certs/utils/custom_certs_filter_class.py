# -*- coding: utf-8 -*-

import django_filters
from django_filters.rest_framework import FilterSet
from certs.models import Certs


class CertsFilter(FilterSet):
    """
    Certs 过滤器类，模糊查询
    """
    domain = django_filters.CharFilter(field_name='domain', lookup_expr='icontains')    # icontains，包含且忽略大小写

    class Meta:
        models = Certs
        fields = ['domain']
