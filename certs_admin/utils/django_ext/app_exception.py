# -*- coding: utf-8 -*-

from certs_admin.utils.django_ext.http_code_enum import HttpCodeEnum


class AppException(Exception):
    code = 0
    message = ''

    def __init__(self, message, code=-1):
        super(Exception, self).__init__()

        self.code = code
        self.message = message

    def get_code(self):
        return self.code

    def get_message(self):
        return self.message


class ForbiddenAppException(AppException):
    def __init__(self, message='暂无权限', code=HttpCodeEnum.Forbidden):
        super(ForbiddenAppException, self).__init__(message, code)


class UnauthorizedAppException(AppException):
    def __init__(self, message='用户未登录', code=HttpCodeEnum.Unauthorized):
        super(UnauthorizedAppException, self).__init__(message, code)


class DataNotFoundAppException(AppException):
    def __init__(self, message='数据不存在', code=HttpCodeEnum.Not_Found):
        super(DataNotFoundAppException, self).__init__(message, code)


class NotSupportedAppException(AppException):
    def __init__(self, message='数据不支持', code=HttpCodeEnum.Not_Support):
        super(NotSupportedAppException, self).__init__(message, code)

class ExistedAppException(AppException):
    def __init__(self, message='数据已存在', code=HttpCodeEnum.Existed):
        super(ExistedAppException, self).__init__(message, code)
