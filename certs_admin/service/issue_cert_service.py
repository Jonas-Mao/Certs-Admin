# -*- coding: utf-8 -*-

import json
import time
import OpenSSL
import requests
import traceback
from acme.messages import ChallengeBody
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.db.models import Q
from certs_admin.config.default_config import DEFAULT_RENEW_DAYS
from certs_admin.utils.django_ext.app_exception import AppException
from certs_admin.utils import datetime_util, fabric_util
from files import domain_util
from certs_admin.utils.acme_util import acme_v2_api
from certs_admin.utils.acme_util.challenge_type import ChallengeType
from certs_admin.utils.acme_util.key_type_enum import KeyTypeEnum
from certs_admin.utils.acme_util.directory_type_enum import DirectoryTypeEnum
from certs_admin.utils.cert_util import cert_common
from certs_admin.enums.challenge_deploy_type_enum import ChallengeDeployTypeEnum
from certs_admin.enums.valid_status_enum import ValidStatus
from certs_admin.enums.ssl_deploy_type_enum import SSLDeployTypeEnum
from certs_admin.enums.dns_type_enum import DnsTypeEnum
from certs_admin.enums.host_auth_type_enum import HostAuthTypeEnum
from certs_admin.utils.open_api.aliyun_domain_api import RecordTypeEnum
from certs_admin.utils.open_api import aliyun_domain_api, tencentcloud_domain_api
from apply_cert.models import ApplyCert
from apply_cert.utils.apply_cert_log import logger
from hosts.models import Host
from hosts.utils.crypto_pass import decrypt_pass
from dnss.models import Dns
from django.contrib.auth import get_user_model

User = get_user_model()


# ******
def issue_cert(
        user,
        domains,
        directory_type=DirectoryTypeEnum.LETS_ENCRYPT,
        key_type=KeyTypeEnum.RSA
):
    """
    提交申请证书
    """
    pkey_pem, csr_pem = acme_v2_api.new_csr_comp(domains=json.dumps(domains))

    issue_cert_row = ApplyCert.objects.create(
        user=user,
        domains=json.dumps(domains),
        ssl_cert_key=pkey_pem.decode('utf-8'),
        directory_type=directory_type,
        key_type=key_type
    )

    return issue_cert_row


# ******
def verify_cert(issue_cert_id, challenge_type):
    """
    验证域名
    """
    issue_cert_row = ApplyCert.objects.get(id=issue_cert_id)

    acme_client = acme_v2_api.get_acme_client(
        directory_type=issue_cert_row.directory_type,
        key_type=issue_cert_row.key_type
    )

    verify_count = 0
    items = get_cert_challenges(issue_cert_id)
    items = json.loads(items.content.decode('utf-8'))  # 查看return返回的JsonResponce对象，并将byte转为str

    for item in items['data']:
        challenge = item['challenge']
        if challenge_type != challenge['type']:
            continue
        challenge_obj = ChallengeBody.from_json(challenge)  # challenge.to_json()之后，再转回类对象
        response, validation = challenge_obj.response_and_validation(acme_client.net.key)
        logger.info(validation)

        acme_client.answer_challenge(challenge_obj, response)
        count = 0
        max_count = 5

        while True:
            count += 1
            status = get_challenge_status(challenge['url'])
            if status == 'valid':
                obj = ApplyCert.objects.get(id=issue_cert_id)
                obj.status = status
                obj.update_time = datetime_util.get_datetime()
                obj.save()
                break
            if count >= max_count:
                raise AppException("域名验证失败！")
            time.sleep(count)

        verify_count += 1

    if verify_count == 0:
        raise AppException("域名验证失败")

    obj = ApplyCert.objects.get(id=issue_cert_id)
    obj.challenge_type = challenge_type
    obj.save()


# ******
def get_cert_challenges(issue_cert_id):
    """
    获取验证方式
    """
    issue_cert_row = ApplyCert.objects.get(id=issue_cert_id)

    pkey_pem = issue_cert_row.ssl_cert_key
    domains = issue_cert_row.domains

    pkey_pem, csr_pem = acme_v2_api.new_csr_comp(
        domains=domains,
        pkey_pem=pkey_pem
    )

    acme_client = acme_v2_api.get_acme_client(
        directory_type=issue_cert_row.directory_type,
        key_type=issue_cert_row.key_type
    )

    orderr = acme_client.new_order(csr_pem)

    lst = []
    for domain, domain_challenges in acme_v2_api.select_challenge(orderr).items():
        for challenge in domain_challenges:
            response, validation = challenge.response_and_validation(acme_client.net.key)
            data = {
                'domain': domain,
                'sub_domain': domain_util.get_subdomain(domain),
                'root_domain': domain_util.get_root_domain(domain),
                'validation': validation,
                'challenge': challenge.to_json()
            }
            lst.append(data)

    res = {'code': 200, 'data': lst, 'msg': '获取成功！'}
    return JsonResponse(res)


# ******
def renew_cert(row_id):
    """
    下载证书到数据库
    """
    issue_cert_row = ApplyCert.objects.get(id=row_id)

    pkey_pem = issue_cert_row.ssl_cert_key
    domains = issue_cert_row.domains

    pkey_pem, csr_pem = acme_v2_api.new_csr_comp(
        domains=domains,
        pkey_pem=pkey_pem,
    )

    acme_client = acme_v2_api.get_acme_client(
        directory_type=issue_cert_row.directory_type,
        key_type=issue_cert_row.key_type
    )

    orderr = acme_client.new_order(csr_pem)

    fullchain_pem = acme_v2_api.perform_http01(acme_client, orderr)
    fullchain_com = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, fullchain_pem)

    cert = cert_common.parse_cert(fullchain_com)

    obj = ApplyCert.objects.get(id=row_id)
    obj.ssl_cert = fullchain_pem
    obj.ssl_start_time = cert.notBefore
    obj.ssl_expire_time = cert.notAfter
    obj.update_time = datetime_util.get_datetime()
    obj.save()

    res = {'code': 200, 'msg': '保存成功！'}
    return JsonResponse(res)


# ******
def get_challenge_status(url):
    """
    获取验证状态
    """
    logger.info(url)

    res = requests.get(url)
    data = res.json()

    logger.info(data)

    return data['status']


# ******
def deploy_verify_file(challenge_deploy_host_id, challenge_deploy_verify_path, challenges):
    """
    部署验证文件
    """
    logger.info(challenges)

    host_row = Host.objects.get(id=challenge_deploy_host_id)
    host = host_row.host
    port = host_row.port
    username = host_row.username
    password = host_row.password or None
    private_key = host_row.private_key or None
    auth_type = host_row.auth_type

    for row in challenges:
        if not row['challenge']['token']:
            raise AppException('token is empty')

        verify_filename = challenge_deploy_verify_path + row['challenge']['token']

        if not verify_filename:
            raise AppException('verify_deploy_filename is empty')

        logger.info("verify_filename: %s" % verify_filename)

        if not row['validation']:
            raise AppException('validation is empty')

        if auth_type == SSLDeployTypeEnum.SSH:
            password = decrypt_pass(password, host)
        else:
            private_key = decrypt_pass(private_key, host)

        if auth_type == HostAuthTypeEnum.PRIVATE_KEY:
            fabric_util.deploy_file_by_key(
                host=host,
                port=port,
                username=username,
                private_key=private_key,
                content=row['validation'],
                remote=verify_filename
            )
        else:
            fabric_util.deploy_file(
                host=host,
                port=port,
                username=username,
                password=password,
                content=row['validation'],
                remote=verify_filename
            )

    res = {'code': 200, 'auth_type': auth_type, 'msg': '部署成功！'}
    return JsonResponse(res)


# ******
def deploy_cert_file(
        deploy_host_id,
        ssl_cert_key,
        deploy_key_file,
        ssl_cert,
        deploy_fullchain_file,
        deploy_reloadcmd
):
    """
    部署证书到服务器
    deploy_key_file: 私钥部署路径
    ssl_cert_key: 私钥内容
    deploy_fullchain_file: 公钥部署路径
    ssl_cert: 公钥内容
    deploy_reloadcmd: 重启命令
    """
    host_row = Host.objects.get(id=deploy_host_id)
    host = host_row.host
    port = host_row.port
    username = host_row.username
    password = host_row.password or None
    auth_type = host_row.auth_type
    private_key = host_row.private_key or None

    if auth_type == SSLDeployTypeEnum.SSH:
        password = decrypt_pass(password, host)
    else:
        private_key = decrypt_pass(private_key, host)

    # deploy key
    if deploy_key_file:
        if auth_type == HostAuthTypeEnum.PRIVATE_KEY:
            fabric_util.deploy_file_by_key(
                host=host,
                port=port,
                username=username,
                private_key=private_key,
                content=ssl_cert_key,
                remote=deploy_key_file
            )
        else:
            fabric_util.deploy_file(
                host=host,
                port=port,
                username=username,
                password=password,
                content=ssl_cert_key,
                remote=deploy_key_file
            )

    # deploy ssl_cert
    if deploy_fullchain_file:
        if auth_type == HostAuthTypeEnum.PRIVATE_KEY:
            fabric_util.deploy_file_by_key(
                host=host,
                port=port,
                username=username,
                private_key=private_key,
                content=ssl_cert,
                remote=deploy_fullchain_file
            )
        else:
            fabric_util.deploy_file(
                host=host,
                port=port,
                username=username,
                password=password,
                content=ssl_cert,
                remote=deploy_fullchain_file
            )

    # reload
    if deploy_reloadcmd:
        if auth_type == HostAuthTypeEnum.PRIVATE_KEY:
            fabric_util.run_command_by_key(
                host=host,
                port=port,
                username=username,
                private_key=private_key,
                command=deploy_reloadcmd
            )
        else:
            fabric_util.run_command(
                host=host,
                port=port,
                username=username,
                password=password,
                command=deploy_reloadcmd
            )


# ******
def add_dns_domain_record(dns_id, issue_cert_id):
    """
    添加dns记录
    """
    dns_row = Dns.objects.get(id=dns_id)
    challenge_list = get_cert_challenges(issue_cert_id)
    challenge_list = json.loads(challenge_list.content)  # JsonResponse to Dict

    for challenge in challenge_list['data']:
        if challenge['challenge']['type'] == ChallengeType.DNS01:
            if challenge['sub_domain'] and challenge['sub_domain'] != 'www':
                record_key = '_acme-challenge.' + challenge['sub_domain']
            else:
                record_key = '_acme-challenge'

            if dns_row.dns_type == DnsTypeEnum.ALIYUN:
                aliyun_domain_api.search_domain_record(
                    access_key_id=dns_row.access_id,
                    access_key_secret=dns_row.access_secret,
                    domain_name=challenge['root_domain'],
                    record_type=RecordTypeEnum.TXT,
                    record_key=record_key,
                    record_value=challenge['validation']
                )
            elif dns_row.dns_type_id == DnsTypeEnum.TENCENT_CLOUD:
                tencentcloud_domain_api.add_domain_record(
                    access_key_id=dns_row.access_key,
                    access_key_secret=dns_row.secret_key,
                    domain_name=challenge['root_domain'],
                    record_type=RecordTypeEnum.TXT,
                    record_key=record_key,
                    record_value=challenge['validation']
                )

    res = {'code': 200, 'msg': '添加成功！'}
    return JsonResponse(res)


# ******
def check_auto_renew(issue_cert_id):
    """
    首次申请，自动判断是否可以自动续期
    """
    issue_cert_row = ApplyCert.objects.get(id=issue_cert_id)

    if issue_cert_row.can_auto_renew:
        ApplyCert.objects.filter(id=issue_cert_id).update(is_auto_renew=True)


# ******
def renew_all_cert():
    """
    更新所有证书
    """
    now = datetime.now()
    notify_expire_time = now + timedelta(days=DEFAULT_RENEW_DAYS)

    apply_cert_rows = ApplyCert.objects.filter(
        Q(is_auto_renew=1) & Q(ssl_expire_time__lte=notify_expire_time) | Q(ssl_expire_time__isnull=True)
    ).order_by('-ssl_expire_time')

    for row in apply_cert_rows:
        try:
            renew_cert_row(row)
        except:
            logger.error(traceback.format_exc())

        time.sleep(2)


# ******
def renew_cert_row(row):
    """
    证书自动续期
    """
    pkey_pem, csr_pem = acme_v2_api.new_csr_comp(domains=row.domains)

    ApplyCert.objects.filter(id=row.id).update(
        ssl_cert_key=pkey_pem.decode('utf-8'),
        ssl_cert='',
        ssl_start_time=None,
        ssl_expire_time=None,
        status=ValidStatus.PENDING
    )

    if row.challenge_deploy_type_id == ChallengeDeployTypeEnum.SSH:
        # 获取验证方式
        items = get_cert_challenges(row.id)
        items = json.loads(items.content.decode('utf-8'))
        # 部署验证文件
        deploy_verify_file(
            challenge_deploy_host_id=row.challenge_deploy_host_id,
            challenge_deploy_verify_path=row.challenge_deploy_verify_path,
            challenges=items['data']
        )
    elif row.challenge_deploy_type_id == ChallengeDeployTypeEnum.DNS:
        # 添加txt记录
        add_dns_domain_record(
            dns_id=row.challenge_deploy_dns_id,
            issue_cert_id=row.id
        )

    # 验证域名
    verify_cert(row.id, row.challenge_type)

    # 保存证书
    renew_cert(row.id)

    # 自动部署
    if row.deploy_type_id == SSLDeployTypeEnum.SSH:
        issue_cert_row = ApplyCert.objects.get(id=row.id)
        deploy_cert_file(
            deploy_host_id=row.deploy_host_id,
            ssl_cert_key=issue_cert_row.ssl_cert_key,
            ssl_cert=issue_cert_row.ssl_cert,
            deploy_key_file=row.deploy_key_file,
            deploy_fullchain_file=row.deploy_fullchain_file,
            deploy_reloadcmd=row.deploy_reloadcmd
        )
