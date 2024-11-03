# -*- coding: utf-8 -*-

import traceback
from datetime import datetime
from django.http import JsonResponse
from apscheduler.schedulers.background import BackgroundScheduler
from certs_admin.enums.config_key_enum import ConfigKeyEnum
from certs_admin.utils import datetime_util
from certs_admin.service import system_service, monitor_service
from certs_apscheduler.scheduler_service import scheduler_config, scheduler_util
from certs_apscheduler.scheduler_service.scheduler_log import apscheduler_logger
from loggers.models import LogScheduler

scheduler = BackgroundScheduler(job_defaults=scheduler_config.JOB_DEFAULTS)


# ****** 1
def init_scheduler():
    scheduler.start()

    # 网站监测任务
    update_monitor_task(datetime.now())

    # 证书监测任务
    scheduler_cron = system_service.get_config(ConfigKeyEnum.SCHEDULER_CRON)
    if not scheduler_cron:
        return

    update_job(scheduler_cron)


# ******
def update_job(cron_exp):
    # Cron定时任务
    minute, hour, day, month, day_of_week = cron_exp.split()

    scheduler.add_job(
        func=run_task,
        trigger='cron',
        minute=minute,
        hour=hour,
        day=day,
        month=month,
        day_of_week=scheduler_util.crontab_compatible_weekday(day_of_week),
        id=scheduler_config.TASK_JOB_ID,
        replace_existing=True
    )


# ****** 2 4
def update_monitor_task(next_run_time):
    monitor_job = scheduler.get_job(scheduler_config.MONITOR_TASK_JOB_ID)

    # 如果下次运行时间比唤起时间早，就替换唤起时间
    if monitor_job and datetime_util.is_greater_than(next_run_time, monitor_job.next_run_time):
        return

    scheduler.add_job(
        func=run_monitor_task,
        next_run_time=next_run_time,
        id=scheduler_config.MONITOR_TASK_JOB_ID,
        replace_existing=True
    )


# ****** 3
def run_monitor_task():
    next_run_time = monitor_service.run_monitor_task()

    if next_run_time:
        update_monitor_task(next_run_time)


# ******
def run_one_monitor_task(monitor_row):
    next_run_time = monitor_service.run_monitor_warp(monitor_row)

    # 监测任务
    if next_run_time:
        update_monitor_task(next_run_time)


#
def get_monitor_task_next_run_time():
    monitor_task = scheduler.get_job(job_id=scheduler_config.MONITOR_TASK_JOB_ID)

    if monitor_task:
        return monitor_task.next_run_time


# ******
def run_task():
    """
    定时任务
    """
    # 开始执行
    log_row = LogScheduler.objects.create()

    msg = '执行成功'
    status = True

    for func in scheduler_config.TASK_LIST:
        try:
            func()
        except Exception as e:
            apscheduler_logger.error(traceback.format_exc())
            status = False
            msg = str(e)

    # 执行完毕
    LogScheduler.objects.filter(
        id=log_row.id
    ).update(
        status=status,
        error_message=msg,
        create_time=datetime_util.get_datetime()
    )


def show_scheduler_jobs(request):
    """
    查看定时任务
    """
    jobs_list = []
    jobs = scheduler.get_jobs()
    for job in jobs:
        jobs_dict = {
            'job_id': job.id,
            'job_name': job.name,
            'job_next_run_time': job.next_run_time,
            'job_func_ref': job.func_ref,
            # 'job.args': job.args,
            # 'job.kwargs': job.kwargs
        }
        jobs_list.append(jobs_dict)

    return JsonResponse(jobs_list, safe=False)