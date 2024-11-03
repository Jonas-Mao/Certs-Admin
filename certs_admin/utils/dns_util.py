# -*- coding: utf-8 -*-

import six
import dns.resolver


def query_domain_cname(domain):
    """
    查询域名的CNAME记录
    """
    lst = []

    query_object = dns.resolver.resolve(
        qname=domain,
        rdtype='CNAME',
        raise_on_no_answer=False
    )

    for query_item in query_object.response.answer:
        for item in query_item.items:
            lst.append(six.text_type(item))

    return lst
