# -*- coding: utf-8 -*-

import six
import paramiko
from fabric import Connection
from certs_admin.config.default_config import DEFAULT_SSH_PORT
from certs_admin.config.env_config import ALLOW_COMMANDS
from certs_admin.utils.django_ext.app_exception import AppException


# 命令白名单
allow_commands = [
    'systemctl reload nginx',
    'systemctl reload openresty',
    'service nginx force-reload',
    'docker exec -id nginx nginx -s reload',
    *ALLOW_COMMANDS     # 用户自定义配置的命令
]

conn_timeout = 15

def deploy_file(host, username, password, content, remote, port=DEFAULT_SSH_PORT):
    """
    远程部署文件
    :param content: 文件内容
    :param remote: 远程路径
    """
    with Connection(
            host=host,
            port=port,
            user=username,
            connect_timeout=conn_timeout,
            connect_kwargs={"password": password}
    ) as conn:
        conn.put(six.StringIO(content), remote)


def run_command(host, username, password, command, port=DEFAULT_SSH_PORT):
    """
    远程运行命令
    """
    if command not in allow_commands:
        raise AppException("命令不被允许，请联系管理员！")

    with Connection(
            host=host,
            port=port,
            user=username,
            connect_timeout=conn_timeout,
            connect_kwargs={"password": password}
    ) as conn:
        conn.run(command, hide=True)


def deploy_file_by_key(host, username, private_key, content, remote, port=DEFAULT_SSH_PORT):
    """
    远程部署文件
    :param private_key: 私钥
    :param content: 文件内容
    :param remote: 远程路径
    """
    with Connection(
            host=host,
            port=port,
            user=username,
            connect_timeout=conn_timeout,
            connect_kwargs={"pkey": _get_paramiko_key(private_key)}
    ) as conn:
        conn.put(six.StringIO(content), remote)


def run_command_by_key(host, username, private_key, command, port=DEFAULT_SSH_PORT):
    """
    远程运行命令
    :param private_key: 私钥
    :param command: 命令
    """
    if command not in allow_commands:
        raise AppException("命令不被允许，请联系管理员")

    with Connection(
            host=host,
            port=port,
            user=username,
            connect_timeout=conn_timeout,
            connect_kwargs={"pkey": _get_paramiko_key(private_key)}
    ) as conn:
        conn.run(command, hide=True)


def _get_paramiko_key(raw_key_content):
    """
    获取paramiko对象秘钥
    :param raw_key_content: 原始秘钥内容
    :return: paramiko 秘钥
    """
    pkey = None
    for pkey_class in (paramiko.RSAKey, paramiko.DSSKey, paramiko.ECDSAKey, paramiko.Ed25519Key):
        try:
            pkey = pkey_class.from_private_key(six.StringIO(raw_key_content))
            break
        except paramiko.SSHException as e:
            pass

    return pkey
