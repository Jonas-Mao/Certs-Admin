# -*- coding: utf-8 -*

"""
企业微信开放API接口
"""

import requests
import json


def get_access_token(corpid, corpsecret):
    url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'

    params = {
        'corpid': corpid,
        'corpsecret': corpsecret
    }

    res = requests.get(url, params=params)

    return res.json()


def send_message(access_token, body):
    url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send'
    params = {'access_token': access_token,}
    body = json.loads(body)
    res = requests.post(url, params=params, json=body)

    return res.json()
