# -*- coding: utf-8 -*-

import json
from loggers.models import LogOperation
from functools import wraps
from django.forms import model_to_dict
from certs_admin.enums.operation_enum import OperationEnum
from django.contrib.auth import get_user_model
User = get_user_model()


def add_operation_log(user_id, table, type_id, before, after):
    """
    添加操作日志
    """
    LogOperation.objects.create(
        user=user_id,
        table=table,
        type_id=type_id,
        before=before,
        after=after
    )


def class_operation_log_decorator(
        model,
        operation_type_id,
        primary_key='id'
):
    """
    用于类视图添加操作日志装饰器
    """
    def outer_wrapper(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            before = None
            after = None

            # before
            if OperationEnum.CREATE == operation_type_id:
                before = None

            elif OperationEnum.UPDATE == operation_type_id:
                before = model.get(id=request.data.get(primary_key))

            elif OperationEnum.DELETE == operation_type_id:
                before = model.get(id=kwargs.get(primary_key))

            ret = func(request, *args, **kwargs)
            ret_json = json.loads(ret.content.decode('UTF-8'))

            if OperationEnum.CREATE == operation_type_id:
                after = model.get(id=ret_json[primary_key])

            if OperationEnum.UPDATE == operation_type_id:
                after = model.get(id=ret_json[primary_key])

            if OperationEnum.DELETE == operation_type_id:
                after = None

            current_user_id = request.user.id
            user_obj = User.objects.get(id=current_user_id)

            datatimeFields = [
                'next_run_time',
                'issue_time',
                'expire_time',
                'create_time',
                'update_time',
                'ssl_start_time',
                'ssl_expire_time'
            ]

            if before:
                before = model_to_dict(before)
                for dt in datatimeFields:
                    if before.get(dt):
                        before[dt] = before[dt].strftime('%Y/%m/%d %H:%M:%S')
            if after:
                after = model_to_dict(after)
                for dt in datatimeFields:
                    if after.get(dt):
                        after[dt] = after[dt].strftime('%Y/%m/%d %H:%M:%S')

            add_operation_log(
                user_id=user_obj,
                table=model.model._meta.db_table,
                type_id=operation_type_id,
                before=before,
                after=after
            )

            return ret

        return wrapper

    return outer_wrapper
    
            return ret

        return wrapper

    return outer_wrapper
