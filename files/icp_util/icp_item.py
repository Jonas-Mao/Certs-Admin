# -*- coding: utf-8 -*-

import json


class ICPItem(object):
    """
    统一的返回格式
    """
    domain = ''
    # 主办单位名称
    name = ''
    # ICP备案/许可证号
    icp = ''

    def to_dict(self):
        return {
            'domain': self.domain,
            'name': self.name,
            'icp': self.icp,
        }

    def __str__(self):
        return '<ICPItem>: ' + json.dumps(self.to_dict(), ensure_ascii=False)
