# -*- coding: utf-8 -*-

import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr
from django.http import JsonResponse


# 默认的发件人
DEFAULT_MAIL_USERNAME = 'ssl_certs@qq.com'
DEFAULT_MAIL_HOST = 'smtp.qq.com'

def get_email_server(mail_host='localhost', mail_port=25):
    """
    获取email服务
    """
    server = ''

    if mail_port == 465:
        server = smtplib.SMTP_SSL(mail_host, mail_port)
    elif mail_port == 587:
        server = smtplib.SMTP(mail_host, mail_port)
        server.starttls()
    else:
        server = smtplib.SMTP(mail_host, mail_port)  # 25

    return server


def send_email(
        subject, content, to_addresses,
        mail_host=DEFAULT_MAIL_HOST, mail_port=25, content_type='plain',
        mail_alias=None, mail_username=None, mail_password=None
):
    """
    :param mail_host: 主机地址
    :param mail_port: 端口
    :param mail_alias: 发件人别名
    :param subject: 主题
    :param content: 内容
    :param to_addresses: 收件人列表
    :param mail_username: 发件人账号
    :param mail_password: 发件人密码
    :param content_type: 内容类型
        - plain: 文本
        - html: 富文本
    """
    mail_username = mail_username or DEFAULT_MAIL_USERNAME
    mail_alias = mail_alias or mail_username

    # 构造邮件
    message = MIMEText(content, content_type, 'utf-8')
    # 邮箱主题
    message['Subject'] = Header(subject, 'utf-8')
    # 昵称,发件人邮箱
    message['From'] = formataddr((mail_alias, mail_username))
    # 显示收件人
    message['To'] = ','.join(formataddr((mail, mail)) for mail in to_addresses)

    server = get_email_server(mail_host, mail_port)

    # 需要登录，否则匿名
    if mail_password:
        try:
            server.ehlo(mail_host)
            server.login(mail_username, mail_password)
        except Exception as e:
            print("连接失败：%s" %e)

    # 发送
    server.sendmail(
        from_addr=mail_username,
        to_addrs=to_addresses,
        msg=message.as_string()
    )

    # 退出
    server.quit()

    return JsonResponse(
        {
            'code': 200,
            'msg': '发送成功！'
        })