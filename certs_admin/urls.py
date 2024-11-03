# -*- coding: utf-8 -*-

from django.contrib import admin
from django.urls import path, re_path, include
from auth_user.views import CustomAuthToken, ChangeUserPasswordView, reset_password
from notify.views import update_notify_status, handle_notify_test, notify_echart
from system.views import update_mail_conf, update_cron_conf, handle_mail_test
from dnss.views import add_dns_domain_record
from loggers.views import clear_all_log_monitor, clear_all_log_operationt, clear_all_log_scheduler, clear_all_log_asynctask
from monitor.views import update_monitor_active, monitor_abnormality_count, monitor_echart
from certs_apscheduler.scheduler_service import show_scheduler_jobs
from certs.views import (
    upate_cert_row,
    update_cert_monitor,
    update_cert_auto_update,
    cert_env_count,
    deploy_cert_trusteeship_file,
    get_cert_trusteeship_deploy_row,
    cert_expire_count,
    certs_echart,
)
from apply_cert.views import (
    issue_cert,
    get_cert_challenges,
    verify_cert,
    deploy_verify_file,
    deploy_cert_file,
    renew_cert,
    renew_issue_cert,
    update_auto_renew,
    single_apply_cert,
    get_allow_commands
)


urlpatterns = [
    re_path('admin/', admin.site.urls),
    re_path('^login/$', CustomAuthToken.as_view()),
    re_path('^change_password/$', ChangeUserPasswordView.as_view()),
    re_path('^upate_cert_row/$', upate_cert_row),
    re_path('^update_cert_monitor/$', update_cert_monitor),
    re_path('^update_cert_auto_update/$', update_cert_auto_update),
    re_path('^reset_password/$', reset_password),
    re_path('^issue_cert/$', issue_cert),
    re_path('^get_cert_challenges/$', get_cert_challenges),
    re_path('^deploy_verify_file/$', deploy_verify_file),
    re_path('^verify_cert/$', verify_cert),
    re_path('^deploy_cert_file/$', deploy_cert_file),
    re_path('^renew_cert/$', renew_cert),
    re_path('^update_auto_renew/$', update_auto_renew),
    re_path('^renew_issue_cert/$', renew_issue_cert),
    re_path('^add_dns_domain_record/$', add_dns_domain_record),
    re_path('^update_notify_status/$', update_notify_status),
    re_path('^update_monitor_active/$', update_monitor_active),
    re_path('^deploy_cert_trusteeship_file/$', deploy_cert_trusteeship_file),
    re_path('^get_cert_trusteeship_deploy_row/$', get_cert_trusteeship_deploy_row),
    re_path('^handle_mail_test/$', handle_mail_test),
    re_path('^handle_notify_test/$', handle_notify_test),
    re_path('^update_mail_conf/$', update_mail_conf),
    re_path('^update_cron_conf/$', update_cron_conf),
    re_path('^cert_env_count/$', cert_env_count),
    re_path('^single_apply_cert/$', single_apply_cert),
    re_path('^get_allow_commands/$', get_allow_commands),
    re_path('^cert_expire_count/$', cert_expire_count),
    re_path('^monitor_abnormality_count/$', monitor_abnormality_count),
    re_path('^certs_echart_data/$', certs_echart),
    re_path('^monitor_echart_data/$', monitor_echart),
    re_path('^notify_echart_data/$', notify_echart),
    re_path('^clear_all_log_operationt/$', clear_all_log_operationt),
    re_path('^clear_all_log_scheduler/$', clear_all_log_scheduler),
    re_path('^clear_all_log_monitor/$', clear_all_log_monitor),
    re_path('^clear_all_log_asynctask/$', clear_all_log_asynctask),
]


from rest_framework import routers
from auth_user.views import UserViewSet
from apply_cert.views import ApplyCertViewSet
from certs.views import CertsViewSet, CertTrusteeshipViewSet, CertTrusteeshipDeployViewSet
from hosts.views import HostViewSet
from dnss.views import DnsViewSet
from envs.views import EnvsViewSet
from loggers.views import LogMonitorViewSet, LogSchedulerViewSet, LogOperationViewSet, AsyncTaskViewSet
from monitor.views import MonitorViewSet
from notify.views import NotifyViewSet
from system.views import SystemViewSet

router = routers.DefaultRouter()
router.register(r'apply_cert', ApplyCertViewSet, basename='apply_cert')
router.register(r'users', UserViewSet, basename='users')
router.register(r'certs', CertsViewSet, basename='certs')
router.register(r'cert_trusteeship', CertTrusteeshipViewSet, basename='cert_trusteeship')
router.register(r'cert_trusteeship_deploy', CertTrusteeshipDeployViewSet, basename='cert_trusteeship_deploy')
router.register(r'hosts', HostViewSet, basename='hosts')
router.register(r'dnss', DnsViewSet, basename='dnss')
router.register(r'envs', EnvsViewSet, basename='envs')
router.register(r'log_monitor', LogMonitorViewSet, basename='log_monitor')
router.register(r'log_operation', LogOperationViewSet, basename='log_operation')
router.register(r'log_scheduler', LogSchedulerViewSet, basename='log_scheduler')
router.register(r'async_task', AsyncTaskViewSet, basename='async_task')
router.register(r'monitor', MonitorViewSet, basename='monitor')
router.register(r'notify', NotifyViewSet, basename='notify')
router.register(r'system', SystemViewSet, basename='system')

urlpatterns += [
    path('api/', include(router.urls))
]
