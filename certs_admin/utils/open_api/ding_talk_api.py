# -*- coding: utf-8 -*-

import requests
import json


def send_message(body):
    """
    发送钉钉群机器人消息
    """
    body = json.loads(body)

    msg = body.get('msg')
    headers = body.get('headers')
    access_token = body.get('access_token')

    url = 'https://oapi.dingtalk.com/robot/send?access_token=%s' % access_token
    res = requests.post(url, json=msg, headers=headers)

    return res.json()
