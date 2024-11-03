# -*- coding: utf-8 -*-

from django.apps import AppConfig


class CertsApschedulerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'certs_apscheduler'

    # 启动定时器
    def ready(self):
        from certs_apscheduler import scheduler_service
        scheduler_service.init_scheduler()
