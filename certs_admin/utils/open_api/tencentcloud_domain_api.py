# -*- coding: utf-8 -*-

import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.dnspod.v20210323 import dnspod_client, models


def add_domain_record(
        access_key_id, access_key_secret,
        domain_name, record_key, record_type, record_value
):
    cred = credential.Credential(
        secret_id=access_key_id,
        secret_key=access_key_secret
    )

    # 实例化一个http选项，可选的，没有特殊需求可以跳过
    httpProfile = HttpProfile()
    httpProfile.endpoint = "dnspod.tencentcloudapi.com"

    # 实例化一个client选项，可选的，没有特殊需求可以跳过
    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile

    # 实例化要请求产品的client对象,clientProfile是可选的
    client = dnspod_client.DnspodClient(cred, "", clientProfile)

    # 实例化一个请求对象,每个接口都会对应一个request对象
    req = models.CreateRecordRequest()
    params = {
        "Domain": domain_name,
        "RecordType": record_type,
        "RecordLine": "默认",
        "Value": record_value,
        "SubDomain": record_key
    }
    req.from_json_string(json.dumps(params))

    resp = client.CreateRecord(req)
    return resp.to_json_string()
