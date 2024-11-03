# -*- coding: utf-8 -*

"""
企业微信开放API接口
"""

import requests
import json


def get_access_token(corpid, corpsecret):
    """
    获取access_token：https://developer.work.weixin.qq.com/document/path/91039
    """
    url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'

    params = {
        'corpid': corpid,
        'corpsecret': corpsecret
    }

    res = requests.get(url, params=params)

    return res.json()


def send_message(access_token, body):
    """
    发送应用消息：https://developer.work.weixin.qq.com/document/path/90236
    """
    url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send'
    params = {'access_token': access_token,}
    body = json.loads(body)
    res = requests.post(url, params=params, json=body)

    return res.json()
