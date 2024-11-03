# -*- coding: utf-8 -*-

import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.dnspod.v20210323 import dnspod_client, models


# ******
def add_domain_record(
        access_key_id, access_key_secret,
        domain_name, record_key, record_type, record_value
):
    """
    示例仅供参考，建议采用更安全的方式：https://cloud.tencent.com/document/product/1278/85305
    密钥可前往控制台获取: https://console.cloud.tencent.com/cam/capi
    https://cloud.tencent.com/document/api/1427/56180
    """
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

    # 返回的resp是一个CreateRecordResponse的实例，与请求对象对应
    resp = client.CreateRecord(req)
    # 输出json格式的字符串回包
    return resp.to_json_string()
