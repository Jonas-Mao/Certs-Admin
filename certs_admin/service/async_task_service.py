# -*- coding: utf-8 -*-

import six
import traceback
from concurrent.futures.thread import ThreadPoolExecutor
from functools import wraps
from loggers.models import AsyncTask
from certs_admin.utils import datetime_util

executor = ThreadPoolExecutor()


def sync_task_decorator(task_name):
    """
    同步任务的日志装饰器
    """
    def outer_wrapper(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):

            current_user_id = request.session.get('user_id')

            try:
                current_user_id = g.user_id
            except Exception as e:
                pass

            # before
            async_task_row = AsyncTask.objects.create(
                user_id=current_user_id,
                task_name=task_name,
                function_name="{}.{}".format(func.__module__, func.__name__),
                start_time=datetime_util.get_datetime()
            )

            result = ''
            error = None

            # execute
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                error = e

            if error:
                result = six.text_type(error)

            data = {
                'status': False if error else True,
                'result': result or '',
                'end_time': datetime_util.get_datetime(),
                'update_time': datetime_util.get_datetime(),
            }

            AsyncTask.objects.filter(id=async_task_row.id).update(**data)

            # 继续抛出异常
            if error:
                raise error
            else:
                return result

        return wrapper

    return outer_wrapper


def submit_task(fn, *args, **kwargs):
    """
    执行异步任务：https://pengshiyu.blog.csdn.net/article/details/114700730
    """
    return executor.submit(fn, *args, **kwargs)


def async_task_decorator(task_name):
    """
    执行异步任务的装饰器
    """
    def outer_wrapper(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):

            current_user_id = request.session.get('user_id')

            # before
            async_task_row = AsyncTask.objects.create(
                user_id=current_user_id,
                task_name=task_name,
                function_name="{}.{}".format(func.__module__, func.__name__),
                start_time=datetime_util.get_datetime()
            )

            # callback
            def done_callback(future):

                is_success = None
                result = ''

                try:
                    result = future.result()
                    is_success = True
                except Exception as e:
                    is_success = False
                    result = e

                if result:
                    result = six.text_type(result)
                else:
                    result = ''

                data = {
                    'status': is_success,
                    'result': result,
                    'end_time': datetime_util.get_datetime(),
                    'update_time': datetime_util.get_datetime(),
                }

                AsyncTask.objects.filter(id=async_task_row.id).update(**data)

            # execute
            ret = submit_task(func, *args, **kwargs)

            # after
            ret.add_done_callback(done_callback)

            return ret

        return wrapper

    return outer_wrapper
