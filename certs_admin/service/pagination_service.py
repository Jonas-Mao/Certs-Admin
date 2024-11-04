# -*- coding: utf-8 -*-

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict


class MyPagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'page_num'
    page_size_query_param = 'page_size'
    max_page_size = 50

    def get_paginated_response(self, data):
        code = 200
        msg = "成功"

        return Response(OrderedDict(
            [
                ('code', code),
                ('msg', msg),
                ('count', self.page.paginator.count),
                ('data', data)
            ]
        ))
