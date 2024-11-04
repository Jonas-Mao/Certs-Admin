# -*- coding: utf-8 -*-

from functools import wraps
from certs_admin.enums.status_enum import StatusEnum
from certs_admin.enums.role_enum import RoleEnum, ROLE_PERMISSION
from certs_admin.utils.django_ext.app_exception import AppException
from rest_framework.authtoken.models import Token
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth import get_user_model
User = get_user_model()


def permission(role=RoleEnum.ADMIN):
    """
    权限控制
    :param role:
    """
    def outer_wrapper(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):      # 原：def wrapper(*args, **kwargs)
            if role is None:
                # 跳过权限校验
                pass
            else:
                # 从请求头中提取token
                token = request.META.get('HTTP_AUTHORIZATION').split()[1]
                try:
                    token = Token.objects.get(key=token)
                    current_user_id = token.user.id
                except Token.DoesNotExist:
                    current_user_id = None

                if not current_user_id:
                    try:
                        raise AppException('用户未登录！')
                    except AppException as e:
                        return JsonResponse({'msg': e.message})

                user_row = User.objects.get(id=current_user_id)

                if not user_row:
                    try:
                        raise AppException('用户不存在！')
                    except AppException as e:
                        return JsonResponse({'msg': e.message})

                if user_row.is_active != StatusEnum.Enabled:
                    try:
                        raise AppException('用户已禁用！')
                    except AppException as e:
                        return JsonResponse({'msg': e.message})

                if not has_role_permission(current_role=user_row.role, need_permission=role):
                    # return HttpResponseForbidden()
                    try:
                        raise AppException('暂无权限访问！')
                    except AppException as e:
                        return JsonResponse({'msg': e.message})

                # 当前用户数据全局可用
                # global current_user_row
                # current_user_row = user_row

            ret = func(request, *args, **kwargs)

            return ret

        return wrapper

    return outer_wrapper


def has_role_permission(current_role, need_permission):
    """
    角色权限判断
    :param current_role:
    :param need_permission:
    """
    if not need_permission:
        return True

    current_permission = []

    for item in ROLE_PERMISSION:
        if item['role'] == current_role:
            current_permission = item['permission']

    return need_permission in current_permission
