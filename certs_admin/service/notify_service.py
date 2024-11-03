# -*- coding: utf-8 -*-

import json
import requests
import traceback
from jinja2 import Template
from datetime import datetime, timedelta
from certs_admin.enums.config_key_enum import ConfigKeyEnum
from certs_admin.enums.event_enum import EventEnum
from certs_admin.enums.notify_type_enum import NotifyTypeEnum
from certs_admin.utils import email_util
from certs_admin.utils.django_ext.app_exception import AppException
from certs_admin.service import system_service, render_service
from certs_admin.utils.open_api import work_weixin_api, ding_talk_api
from django.db.models import Q
from django.forms.models import model_to_dict
from notify.models import Notify
from notify.utils.notify_log import logger
from certs.models import Certs, CertTrusteeship
from django.contrib.auth import get_user_model
User = get_user_model()

# 通知参数配置
NOTIFY_CONFIGS = [
    {
        'event_id': EventEnum.SSL_CERT_EXPIRE,
        'email_template': 'cert-email.html',
        'email_subject': '[Certs Admin]证书过期提醒',
    },
    {
        'event_id': EventEnum.MONITOR_EXCEPTION,
        'email_template': 'monitor-email.html',
        'email_subject': '[Certs Admin]监控异常提醒',
    },
    {
        'event_id': EventEnum.MONITOR_EXCEPTION_RESTORE,
        'email_template': 'monitor-restore-email.html',
        'email_subject': '[Certs Admin]监控异常恢复提醒',
    },
    {
        'event_id': EventEnum.SSL_CERT_FILE_EXPIRE,
        'email_template': 'cert-email.html',
        'email_subject': '[Certs Admin]托管证书到期提醒',
    }
]


# ******
def get_notify_config(event_id):
    """
    获取通知参数
    """
    for config in NOTIFY_CONFIGS:
        if config['event_id'] == event_id:
            return config


# ******
def notify_all_event():
    """
    触发所有通知事件
    """
    rows = Notify.objects.filter(
        status=1,
        event_id__in=(
            EventEnum.SSL_CERT_EXPIRE,
            EventEnum.SSL_CERT_FILE_EXPIRE,
            EventEnum.MONITOR_EXCEPTION
        )
    )

    success = 0
    for row in rows:
        try:
            notify_user_about_some_event(row)
        except Exception as e:
            logger.error(traceback.format_exc())

        success = success + 1

    return success


# ******
def notify_user_about_some_event(notify_row):
    """
    事件触发通知
    """
    if notify_row.event_id == EventEnum.SSL_CERT_EXPIRE:
        # SSL证书到期
        return notify_user_about_cert_expired(notify_row)
    elif notify_row.event_id == EventEnum.SSL_CERT_FILE_EXPIRE:
        # 托管证书到期
        return notify_user_about_cert_file_expired(notify_row)
    else:
        raise AppException("{} Not Support！".format(notify_row.event_id))


# ******
def notify_user_about_cert_expired(notify_row):
    """
    SSL证书过期
    """
    now = datetime.now()
    notify_expire_time = now + timedelta(days=notify_row.expire_days)

    # 多对多分组id
    notify = Notify.objects.get(id=notify_row.id)
    envs_rows_list = notify.envs.all()
    envs_rows_ids = [row.id for row in envs_rows_list]

    query = Certs.objects.filter(is_monitor=1)

    if envs_rows_ids:
        query = query.filter(Q(user__id=notify_row.user.id) & Q(envs__id__in=(envs_rows_ids)))
    else:
        query = query.filter(user__id=notify_row.user.id)

    rows = query.filter(
        Q(expire_time__lte=notify_expire_time) & Q(expire_time__gte=now)
    ).order_by('expire_time', '-id')

    lst = [model_to_dict(
        row,
        fields=[
            'domain',
            'status',
            'issue_time',
            'expire_time',
            'remaining_days',
            'update_time',
            'is_monitor',
            'comment',
            'envs'
        ]
    ) for row in rows]

    if len(lst) > 0:
        return notify_user(notify_row, lst)


# ******
def notify_user_about_cert_file_expired(notify_row):
    """
    托管证书到期
    """
    now = datetime.now()

    notify_expire_time = now + timedelta(days=notify_row.expire_days)

    rows = CertTrusteeship.objects.filter(
        Q(ssl_expire_time__lte=notify_expire_time) & Q(ssl_expire_time__gte=now)
    ).order_by(
        'ssl_expire_time',
        '-id'
    )

    lst = [model_to_dict(
        row,
        fields=[
            'domain',
            'ssl_start_time',
            'ssl_expire_time',
            'remaining_days',
            'update_time',
            'comment',
            'envs'
        ]
    ) for row in rows]

    for row in lst:
        row['issue_time'] = row['ssl_start_time']
        row['expire_time'] = row['ssl_expire_time']

    if len(lst) > 0:
        return notify_user(notify_row, lst)


# ******
def notify_user(notify_row, rows, data=None):
    """
    通知用户
    """
    data = data if data else {}

    if notify_row.notify_choice == NotifyTypeEnum.Email:
        notify_config = get_notify_config(notify_row.event_id)

        if not notify_config:
            raise AppException('邮件通知模板未配置')

        mail_value = notify_row.value_raw.replace("'", '"')
        mail_value = json.loads(mail_value)
        mail_list = mail_value.get('mail_list')

        return notify_user_by_email(
            template=notify_config['email_template'],
            subject=notify_config['email_subject'],
            data={**data, 'list': rows},
            email_list=mail_list
        )

    elif notify_row.notify_choice == NotifyTypeEnum.WORK_WEIXIN:
        return notify_user_by_work_weixin(notify_row=notify_row, data={**data, 'list': rows})

    elif notify_row.notify_choice == NotifyTypeEnum.DING_TALK:
        return notify_user_by_ding_talk(notify_row=notify_row, data={**data, 'list': rows})

    elif notify_row.notify_choice == NotifyTypeEnum.WebHook:
        return notify_user_by_webhook(
            notify_row=notify_row,
            data={**data, 'list': rows}
        )
    else:
        print("Notify type is not support！")


# ******
def notify_user_by_email(
        template,
        subject,
        data,
        email_list,
):
    """
    通过邮件通知用户证书到期
    """
    if not email_list or len(email_list) == 0:
        print("Mail list is empty！")
        return

    content = render_service.render_template(
        template=template,
        data=data
    )

    config = system_service.get_system_config()

    email_util.send_email(
        mail_host=config[ConfigKeyEnum.MAIL_HOST],
        mail_port=int(config[ConfigKeyEnum.MAIL_PORT]),
        mail_alias=config[ConfigKeyEnum.MAIL_ALIAS],
        subject=subject,
        content=content,
        to_addresses=email_list,
        mail_username=config[ConfigKeyEnum.MAIL_USERNAME],
        mail_password=config[ConfigKeyEnum.MAIL_PASSWORD],
        content_type='html'
    )


# ******
def notify_user_by_work_weixin(notify_row, data):
    """
    发送企业微信消息
    """
    notify_row_dict = model_to_dict(notify_row)

    notify_row_value = notify_row_dict.get('value_raw')
    notify_row_value = notify_row_value.replace("'", '"')
    notify_row_value = json.loads(notify_row_value)

    token = work_weixin_api.get_access_token(
        notify_row_value.get('weixin_corpid'),
        notify_row_value.get('weixin_corpsecret')
    )

    # 支持模板变量
    # template = Template(json.dumps(notify_row_value.get('weixin_body')))
    # weixin_body = template.render(data)

    event_id = notify_row_dict.get('event_id')
    event_name = 'SSL证书' if event_id == 1 else '托管证书'

    for i in data['list']:
        weixin_body = notify_row_value.get('weixin_body')
        weixin_body['text']['content'] = f"{event_name}过期提醒：\n【 {i['domain']} 】剩余【 {i['remaining_days']} 】天，请及时进行更新！"
        weixin_body = json.dumps(weixin_body)
        work_weixin_api.send_message(token.get('access_token'), weixin_body)


# ******
def notify_user_by_ding_talk(notify_row, data):
    """
    发送钉钉消息
    """
    notify_row_dict = model_to_dict(notify_row)

    notify_row_value = notify_row_dict.get('value_raw')
    notify_row_value = notify_row_value.replace("'", '"')
    notify_row = json.loads(notify_row_value)

    # 支持模板变量
    # template = Template(json.dumps(notify_row.get('dingtalk_body')))
    # dingtalk_body = template.render(data)

    event_id = notify_row_dict.get('event_id')
    event_name = 'SSL证书' if event_id == 1 else '托管证书'

    for i in data['list']:
        dingtalk_body = notify_row.get('dingtalk_body')
        dingtalk_body['msg']['text']['content'] = f"{event_name}过期提醒：\n【 {i['domain']} 】剩余【 {i['remaining_days']} 】天，请及时进行更新！"
        dingtalk_body = json.dumps(dingtalk_body)
        ding_talk_api.send_message(dingtalk_body)


# ******
def notify_user_about_monitor_exception(monitor_row, error):
    """
    监控异常通知
    """
    rows = Notify.objects.filter(
        status=1,
        event_id=EventEnum.MONITOR_EXCEPTION
    )
    for row in rows:
        try:
            notify_user(notify_row=row, rows=rows, data={'monitor_row': monitor_row, 'error': str(error)})
        except Exception as e:
            print(e)


# ******
def notify_user_about_monitor_exception_restore(monitor_row):
    """
    监控异常恢复通知
    """
    rows = Notify.objects.filter(
        status=1,
        event_id=EventEnum.MONITOR_EXCEPTION_RESTORE
    )

    for row in rows:
        try:
            notify_user(notify_row=row, rows=rows, data={'monitor_row': monitor_row})
        except Exception as e:
            print(e)


def notify_user_by_webhook(notify_row, data):
    """
    通过webhook方式通知用户
    """
    notify_row_dict = model_to_dict(notify_row)
    notify_row_value = notify_row_dict.get('value_raw')
    notify_row_value = notify_row_value.replace("'", '"')
    notify_row_value = json.loads(notify_row_value)

    if not notify_row_value.get('webhook_url'):
        print("webhook url未设置")
        return

    # 支持模板变量
    template = Template(json.dumps(notify_row_value.get('webhook_body')))
    body_render = template.render(data)

    res = requests.request(
        method=notify_row_value.get('webhook_method'),
        url=notify_row_value.get('webhook_url'),
        headers=notify_row_value.get('webhook_headers'),
        data=body_render.encode('utf-8'))

    res.encoding = res.apparent_encoding
    return res.text


def get_notify_row_value(user_id, event_id):
    """
    获取通知配置
    """
    notify_row = Notify.objects.filter(
        type_id=event_id,
        user__id=user_id
    )

    if not notify_row:
        return None

    if not notify_row.value_raw:
        return None

    return notify_row.value_raw


def get_notify_email_list(user_id):
    """
    获取通知配置 - 邮箱列表
    """
    notify_row_value = get_notify_row_value(user_id, NotifyTypeEnum.Email)

    if not notify_row_value:
        return None

    email_list = notify_row_value.get('email_list')

    if not email_list:
        return None

    return email_list


def get_notify_webhook_row(user_id):
    """
    获取通知配置 - webhook
    """
    return get_notify_row_value(user_id, NotifyTypeEnum.WebHook)
