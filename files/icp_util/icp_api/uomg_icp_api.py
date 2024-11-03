# -*- coding: utf-8 -*-

import requests
from files.icp_util.icp_item import ICPItem


def get_icp_from_uomg(domain):
    """
    {
        "code": 1,
        "domain": "baidu.com",
        "icp": "京ICP证030173号"
    }
    {
        "code": 1,
        "domain": "baidu1.com",
        "icp": "未备案"
    }
    """
    # url = 'https://api.uomg.com/api/icp'          # 已禁用
    url = 'https://api.leafone.cn/api/icp'

    data = {
        "domain": domain
    }

    # 发送GET请求
    response = requests.get(url, params=data, timeout=5)
    data = response.json()

    # if data.get('icp') == '未备案':
        # raise Exception('未备案')

    item = ICPItem()
    item.name = data.get('')
    item.icp = data.get('icp')
    return item.to_dict()


if __name__ == '__main__':
    print(get_icp_from_uomg('qq.com').to_dict())
