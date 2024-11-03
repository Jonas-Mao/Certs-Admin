# -*- coding: utf-8 -*-

import requests
import json


def send_message(body):
    """
    发送钉钉群机器人消息
    return:
    {
        'errcode': 0,
        'errmsg': 'ok'
    }
    """
    body = json.loads(body)

    msg = body.get('msg')
    headers = body.get('headers')
    access_token = body.get('access_token')

    url = 'https://oapi.dingtalk.com/robot/send?access_token=%s' % access_token
    res = requests.post(url, json=msg, headers=headers)

    return res.json()


'''
# 企业应用方式发送消息-1
# def get_access_token(appkey, appsecret):
#     """
#     获取access_token：https://open.dingtalk.com/document/orgapp/obtain-orgapp-token
#     :return：
#     {
#         "errcode": 0,
#         "access_token": "xxx",
#         "errmsg": "ok",
#         "expires_in": 7200
#     }
#     """
#     url = 'https://oapi.dingtalk.com/gettoken'
#     params = {
#         'appkey': appkey,
#         'appsecret': appsecret
#     }
#
#     res = requests.get(url, params=params)
#
#     return res.json()


# 企业应用方式发送消息-2
# def send_message(access_token, body):
#     """
#     发送应用消息：https://open.dingtalk.com/document/orgapp/asynchronous-sending-of-enterprise-session-messages
#     :return：
#     {
#         "errcode":0,
#         "task_id":256271667526,
#         "request_id":"4jzllmte0wau"
#     }
#     """
#     url = 'https://oapi.dingtalk.com/topapi/message/corpconversation/asyncsend_v2'
#
#     params = {
#         'access_token': access_token,
#     }
#
#     res = requests.post(url, params=params, json=body)
#
#     return res.json()
'''