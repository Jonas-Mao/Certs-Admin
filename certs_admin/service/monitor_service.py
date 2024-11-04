# -*- coding: utf-8 -*-

import json
from datetime import datetime, timedelta
from functools import wraps
import six
import requests
from time import sleep
from certs_admin.config.default_config import USER_AGENT
from certs_admin.enums.monitor_status_enum import MonitorStatusEnum
from certs_admin.enums.monitor_type_enum import MonitorTypeEnum
from certs_admin.service import notify_service, file_service, async_task_service
from certs_apscheduler.scheduler_service import scheduler_main
from certs_admin.utils import datetime_util, file_util
from monitor.models import Monitor
from loggers.models import LogMonitor, LogScheduler, LogOperation, AsyncTask


def monitor_log_decorator(func):
    @wraps(func)
    def wrapper(monitor_row, *args, **kwargs):
        # 执行
        result = ''
        error = None
        start_time = datetime.now()

        try:
            result = func(monitor_row, *args, **kwargs)
        except Exception as e:
            error = e

        if error:
            result = six.text_type(error)

        LogMonitor.objects.create(
            monitor_id=monitor_row.id,
            monitor_type=monitor_row.monitor_type,
            create_time=start_time,
            result=result or '-',
            status=MonitorStatusEnum.ERROR if error else MonitorStatusEnum.SUCCESS,
        )

        if error:
            raise error
        else:
            return result

    return wrapper


def monitor_notify_decorator(func):
    @wraps(func)
    def wrapper(monitor_row, *args, **kwargs):
        result = None
        error = None

        try:
            result = func(monitor_row, *args, **kwargs)
        except Exception as e:
            error = e

        if error:
            handle_monitor_exception(monitor_row, error)
            raise error
        else:
            handle_monitor_exception_restore(monitor_row)

            return result

    return wrapper


def handle_monitor_exception(monitor_row, error):
    if monitor_row.retries > 0 and is_between_allow_error_count(monitor_row):
        return
    notify_service.notify_user_about_monitor_exception(monitor_row, error)


def handle_monitor_exception_restore(monitor_row):
    if monitor_row.status != MonitorStatusEnum.ERROR:
        return

    if monitor_row.retries > 0 and is_between_allow_error_count(monitor_row):
        return

    notify_service.notify_user_about_monitor_exception_restore(monitor_row)


def run_monitor_task():
    monitor_rows = Monitor.objects.filter(
        is_active=1,
        next_run_time__lt=datetime_util.get_datetime()
    ).order_by('next_run_time')

    for monitor_row in monitor_rows:
        run_monitor_warp(monitor_row)

    monitor_row = Monitor.objects.filter(is_active=1).order_by('next_run_time')

    if monitor_row:
        for monitor in monitor_row:
            return monitor.next_run_time

def run_monitor_warp(monitor_row):
    error = None

    try:
        run_monitor(monitor_row)
    except Exception as e:
        error = e

    # 下次运行时间
    next_run_time = datetime.now() + timedelta(minutes=monitor_row.interval)

    # 同步任务
    Monitor.objects.filter(id=monitor_row.id).update(
        next_run_time=next_run_time,
        status=MonitorStatusEnum.ERROR if error else MonitorStatusEnum.SUCCESS,
    )

    if monitor_row.is_active:
        return next_run_time


@monitor_log_decorator
@monitor_notify_decorator
def run_monitor(monitor_row):
    if monitor_row.monitor_type == MonitorTypeEnum.HTTP:
        run_http_monitor(
            url=monitor_row.url,
            method=monitor_row.method,
            timeout=int(monitor_row.timeout),
            retries=int(monitor_row.retries)
        )


def run_http_monitor(url, method='GET', timeout=3, retries=3):
    res = None
    for _ in range(retries):
        try:
            res = requests.request(
                method=method,
                url=url,
                timeout=timeout,
                headers={"User-Agent": USER_AGENT}
            )
            if res.status_code == 200:
                return res.text
        except requests.exceptions.RequestException:
            pass

        sleep(1)

    if res.status_code != 200:
        res.raise_for_status()

    return res.text


def is_between_allow_error_count(monitor_row):
    # 检查连续失败次数是否大于最大允许失败次数，增加容错
    rows = LogMonitor.objects.filter(monitor_id=monitor_row.id).order_by('-id')

    error_count = len([row for row in rows if row.status == MonitorStatusEnum.ERROR])

    return error_count <= monitor_row.retries


def run_init_monitor_task_async(user_id):

    rows = Monitor.objects.get(user__id=user_id)

    for row in rows:
        scheduler_main.run_one_monitor_task(row)
