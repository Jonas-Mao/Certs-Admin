# -*- coding: utf-8 -*-

import json
from certs_admin.utils.django_ext.app_exception import AppException
from rest_framework.authtoken.models import Token
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as user_login
from django.contrib.auth import authenticate, get_user_model
User = get_user_model()


def login(request):
    """
    用户登录
    """
    if request.method != "POST":
        try:
            raise AppException('禁止%s方式访问！' % request.method)
        except AppException as e:
            return JsonResponse({'Code': 405, 'Error': e.message})
    try:
        data = json.loads(request.body)
    except:
        data = {'username': '', 'password': ''}
    username = data.get('username')
    password = data.get('password')
    user = authenticate(username=username, password=password)
    if not user:
        try:
            raise AppException('账号不存在！')
        except AppException as e:
            return JsonResponse({'Error': e.message})
    if not user.is_active:
        try:
            raise AppException('账号不可用！')
        except AppException as e:
            return JsonResponse({'Error': e.message})
    token, created = Token.objects.get_or_create(user=user)
    user_login(request, user)

    res = {'code': 200, 'user_id': user.id, 'username': user.username, 'token': token.key, 'msg': '登录成功！'}
    return JsonResponse(res)


def register(request):
    """
    用户注册
    """
    if request.method != "POST":
        try:
            raise AppException('禁止%s方式访问！' % request.method)
        except AppException as e:
            return JsonResponse({'Code': 405, 'Error': e.message})
    try:
        data = json.loads(request.body)
    except:
        data = {'username': '', 'password': '', 'password_repeat': '', 'email': ''}

    username = data.get('username')
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    email = data.get('email')
    user = User.objects.filter(username=username)

    if user:
        try:
            raise AppException('用户已存在')
        except AppException as e:
            return JsonResponse({'Error': e.message})
    if password != confirm_password:
        try:
            raise AppException('两次密码不一致')
        except AppException as e:
            return JsonResponse({'Error': e.message})
    if username and password:
        data = User.objects.create(
            username=username,
            password=make_password(password),
            email=email
        )
        if data:
            res = {'code': 200, 'username': username, 'msg': '创建成功！'}
            return JsonResponse(res)

    return HttpResponse('用户名或密码不能为空！')


def send_code():
    """
    发送验证码
    """
    raise AppException('暂未使用')


@login_required()
def change_password(request):
    """
    修改密码
    """
    if request.method != "PUT":
        try:
            raise AppException('禁止%s方式访问！' % request.method)
        except AppException as e:
            return JsonResponse({'Code': 405, 'Error': e.message})

    data = json.loads(request.body)

    username = data.get('username')
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    user = User.objects.get(username=username)

    if not user.check_password(old_password):
        try:
            raise AppException('原密码输入有误！')
        except AppException as e:
            return JsonResponse({'Error': e.message})

    if new_password != confirm_password:
        try:
            raise AppException('两次密码不一致！')
        except AppException as e:
            return JsonResponse({'Error': e.message})

    user.set_password(new_password)
    user.save()

    res = {'code': 200, 'msg': '修改成功！'}
    return JsonResponse(res)
