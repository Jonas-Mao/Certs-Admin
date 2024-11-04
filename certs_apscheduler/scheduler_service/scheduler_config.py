# -*- coding: utf-8 -*-

from certs_admin.utils import uuid_util
from certs_admin.service import notify_service, issue_cert_service, cert_service


JOB_DEFAULTS = {
    'misfire_grace_time': None, 
    'coalesce': True, 
    'max_instances': 1
}

TASK_JOB_ID = uuid_util.get_uuid()

MONITOR_TASK_JOB_ID = uuid_util.get_uuid()

TASK_LIST = [
    cert_service.update_all_cert,
    issue_cert_service.renew_all_cert,
    notify_service.notify_all_event,
]
