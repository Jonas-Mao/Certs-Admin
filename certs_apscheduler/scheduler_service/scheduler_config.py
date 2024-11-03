# -*- coding: utf-8 -*-

from certs_admin.utils import uuid_util
from certs_admin.service import notify_service, issue_cert_service, cert_service


JOB_DEFAULTS = {
    'misfire_grace_time': None,     # 默认值 1
    'coalesce': True,               # 默认值 True
    'max_instances': 1              # 默认值 1
}

TASK_JOB_ID = uuid_util.get_uuid()

MONITOR_TASK_JOB_ID = uuid_util.get_uuid()

# 任务列表
TASK_LIST = [
    # 更新证书信息
    # cert_service.update_all_cert,
    # 更新所有申请证书
    # issue_cert_service.renew_all_cert,
    # 触发通知
    notify_service.notify_all_event,
]
