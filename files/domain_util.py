# -*- coding: utf-8 -*-

import io
import re
import tldextract
from tldextract.remote import looks_like_ip

from certs_admin.utils import file_util
from files import text_util
from certs_admin.utils.cert_util import cert_consts


class ParsedDomain(object):
    """
    解析后的domain数据
    """
    domain = ''
    root_domain = ''
    group_name = ''
    port = 0
    alias = ''
    tags = None


def parse_domain(domain):
    """
    解析域名信息
    """
    ret = re.match('((http(s)?:)?//)?(?P<domain>[\\w\\._:-]+)/?.*?', domain)
    if ret:
        return ret.groupdict().get("domain")
    else:
        return None


def parse_domain_from_csv_file(filename):
    """
    读取csv文件 适合完整导入
    :param filename:
    :return: ParsedDomain
    """
    with io.open(filename, 'r', encoding='utf-8') as f:
        # 标题
        first_line = f.readline()
        keys = [filed.strip() for filed in first_line.split(',')]

        # 内容字段
        for line in f.readlines():
            values = [filed.strip() for filed in line.split(',')]
            item = dict(zip(keys, values))

            domain = parse_domain(item.get('域名', ''))
            if ':' in domain:
                domain, port = domain.split(":")
            else:
                # SSL默认端口
                port = cert_consts.SSL_DEFAULT_PORT

            alias = item.get('备注', '').strip(' -')
            group_name = item.get('分组', '').strip(' -')

            # SSL端口
            port = item.get('端口') or port or cert_consts.SSL_DEFAULT_PORT

            # 标签
            tags = item.get('标签') or None
            if tags:
                tags = [tag.strip() for tag in tags.split("、") if tag and tag.strip() and tag.strip() != '-']

            if domain:
                item = ParsedDomain()

                item.domain = domain
                item.root_domain = get_root_domain(domain)
                item.port = int(port)
                item.alias = alias
                item.group_name = group_name
                item.tags = tags

                yield item


def parse_domain_from_txt_file(filename):
    """
    读取txt文件 适合快速导入
    :param filename:
    :return: ParsedDomain
    """
    with io.open(filename, 'r', encoding='utf-8') as f:
        for line in f.readlines():

            domain = parse_domain(line.strip())

            if ':' in domain:
                domain, port = domain.split(":")
            else:
                # SSL默认端口
                port = cert_consts.SSL_DEFAULT_PORT

            if domain:
                item = ParsedDomain()

                item.domain = domain
                item.root_domain = get_root_domain(domain)
                item.port = int(port)
                item.alias = ''
                item.group_name = ''

                yield item


def parse_domain_from_file(filename, field_mapping):
    """
    解析域名文件的工厂方法
    :param filename:
    :return: ParsedDomain
    """
    file_type = file_util.get_filename_ext(filename)
    rows = file_util.read_data_from_file(filename)

    if file_type == 'txt':
        rows = [
            {'domain': parse_domain(row.strip())}
            for row in rows
        ]
    else:
        rows = file_util.convert_to_import(rows, field_mapping)

    for item in rows:
        domain = parse_domain(item['domain'])

        if ':' in domain:
            domain, port = domain.split(":")
        else:
            port = cert_consts.SSL_DEFAULT_PORT     # SSL默认端口

        item['domain'] = domain
        item['root_domain'] = get_root_domain(domain)

        if not item.get('port'):
            item['port'] = port

        # 标签
        item['tags'] = text_util.split_string(item.get('tags_str'))

    return rows


# ******
def extract_domain(domain):
    """
    解析域名
    """
    return tldextract.extract(domain)


# ******
def get_root_domain(domain):
    """
    解析出域名和顶级后缀
    """
    extract_result = extract_domain(domain)
    return extract_result.registered_domain


def get_subdomain(domain):
    """
    解析出子域名前缀
    """
    extract_result = extract_domain(domain)
    return extract_result.subdomain


# ******
def is_ipv4(ip):
    """
    检测字符串是否为ipv4地址
    :return: bool
    """
    return looks_like_ip(ip)


def encode_hostname(hostname):
    """
    编码中文域名，英文域名原样返回
    :param hostname: str 中文域名
    :return: str
    """
    return hostname.encode('idna').decode('ascii')


def verify_cert_common_name(common_name, domain):
    """
    验证证书
    所有品牌的通配符证书 SSL只能支持域名本身及下一级的所有子域名，而不是无限级支持子域名。
    :param common_name:
    :param domain:
    :return:
    """
    if '*' in common_name:
        # 通配符 SSL 证书
        common_name_root_domain = get_domain_parent(common_name)
        root_domain = get_domain_parent(domain)
        return common_name_root_domain == root_domain \
               or common_name_root_domain == domain
    else:
        # 普通证书
        return common_name == domain


def get_domain_parent(domain):
    """
    获取父级域名
    :param domain:
    :return:
    eg:
    www.chinafruitime.com => chinafruitime.com
    blog.www.chinafruitime.com => www.chinafruitime.com
    """
    if not domain:
        return ''

    first_dot_index = domain.find('.')

    if first_dot_index < 0:
        return ''

    return domain[first_dot_index + 1:]


if __name__ == '__main__':
    # print(get_root_domain("*.juejin.cn"))
    print(get_subdomain("chinafruitime.com"))
