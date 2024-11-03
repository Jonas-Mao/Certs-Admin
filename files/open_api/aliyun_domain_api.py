# -*- coding: utf-8 -*-

import json
from django.http import JsonResponse
from aliyunsdkalidns.request.v20150109.AddDomainRecordRequest import AddDomainRecordRequest
from aliyunsdkalidns.request.v20150109.DescribeDomainRecordsRequest import DescribeDomainRecordsRequest
from aliyunsdkcore.auth.credentials import AccessKeyCredential
from aliyunsdkcore.client import AcsClient
import logging
logger = logging.getLogger('certs-admin')


class RecordTypeEnum:
    """
    记录类型枚举  ref: https://help.aliyun.com/zh/dns/dns-record-types
    """
    A = 'A'
    TXT = 'TXT'


def search_domain_record(
        access_key_id,
        access_key_secret,
        domain_name,
        record_key,
        record_type,
        record_value
):
    client = AcsClient(access_key_id, access_key_secret, 'cn-hangzhou')

    # 创建请求并设置参数
    request = DescribeDomainRecordsRequest()
    request.set_accept_format('json')
    request.set_DomainName('ai-site.cn')

    # 发送请求并接收响应
    response = client.do_action_with_exception(request)
    response = json.loads(str(response, encoding='utf-8'))
    records = response.get('DomainRecords')

    for record in records['Record']:
        if record['Type'] == 'TXT':
            # 查询记录
            if record['RR'] == '_acme-challenge' or record['RR'] == f"_acme-challenge.{domain_name}" and record['Value'] == record_value:
                res = {'code': 500, 'msg': f"{record['RR']}:{record['Value']} 已存在！"}
                return JsonResponse(res)

            # 添加记录
            add_domain_record(
                access_key_id,
                access_key_secret,
                domain_name,
                record_key,
                record_type,
                record_value
            )


def add_domain_record(
        access_key_id,
        access_key_secret,
        domain_name,
        record_key,
        record_type,
        record_value
):
    """
    添加域名解析记录
    https://next.api.aliyun.com/api-tools/sdk/Alidns?version=2015-01-09&language=python&tab=primer-doc
    https://next.api.aliyun.com/api/Alidns/2015-01-09/AddDomainRecord?sdkStyle=old&tab=DEMO&lang=PYTHON
    """
    logger.info("%s", {
        'access_key_id': access_key_id,
        'access_key_secret': access_key_secret,
        'domain_name': domain_name,
        'record_key': record_key,
        'record_type': record_type,
        'record_value': record_value,
    })

    credentials = AccessKeyCredential(
        access_key_id=access_key_id,
        access_key_secret=access_key_secret
    )

    # use STS Token
    # credentials = StsTokenCredential(os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID'], os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET'], os.environ['ALIBABA_CLOUD_SECURITY_TOKEN'])
    client = AcsClient(region_id='cn-beijing', credential=credentials)

    request = AddDomainRecordRequest()
    request.set_accept_format('json')
    request.set_DomainName(domain_name)
    request.set_RR(record_key)
    request.set_Type(record_type)
    request.set_Value(record_value)
    response = client.do_action_with_exception(request)

    # 处理已添加的提示
    if 'RecordId' in str(response):
        print(str(response, encoding='utf-8'))
    else:
        print("Failed to add DNS record.")
