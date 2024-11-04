# -*- coding: utf-8 -*-

import json
from certs_admin.utils import secret_util
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from certs_admin.enums.operation_enum import OperationEnum
from certs_admin.service.operation_service import class_operation_log_decorator, def_operation_log_decorator
from rest_framework import filters
from rest_framework.viewsets import ModelViewSet
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions
from certs_admin.service import auth_service
from certs_admin.enums.role_enum import RoleEnum
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from auth_user.serializers import UserSerializer
from django.contrib.auth import get_user_model
User = get_user_model()

from auth_user.utils.auth_user_log import logger


class UserViewSet(ModelViewSet):
    """
    用户管理
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ('username',)
    filter_fields = ('username', 'role')

    def get_permissions(self):
        if self.action == 'list':
            return [permissions.IsAuthenticated()]
        if self.action == 'retrieve':
            return [permissions.IsAuthenticated()]
        if self.action == 'create':
            return [permissions.IsAdminUser()]
        if self.action == 'update':
            return [permissions.IsAdminUser()]
        if self.action == 'destroy':
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'code': 200,
            'data': serializer.data,
            'msg': '获取成功！'
        })

    @method_decorator(class_operation_log_decorator(
        model=User.objects,
        operation_type_id=OperationEnum.UPDATE,
        primary_key='id')
    )
    def update(self, request, pk=None, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        is_active = request.data.get('is_active')
        User.objects.filter(
            id=pk
        ).update(
            is_active=is_active
        )
        code = 200 if is_active else 201
        msg = '用户已启用！' if is_active else '用户已禁用！'

        logger.info(f"({pk} {msg})")

        res = {'code': code, 'id': pk, 'msg': msg}
        return JsonResponse(res)

    @method_decorator(class_operation_log_decorator(
        model=User.objects,
        operation_type_id=OperationEnum.DELETE,
        primary_key='pk')
    )
    def destroy(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        res = {'code': 200, 'msg': '删除成功！'}
        return JsonResponse(res)

    @method_decorator(class_operation_log_decorator(
        model=User.objects,
        operation_type_id=OperationEnum.CREATE,
        primary_key='id')
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        username = request.data.get('username')
        password = make_password(request.data.get('password'))
        role = request.data.get('role')
        user_obj = User.objects.create(username=username, password=password, role=role)

        res = {'code': 200, 'id': user_obj.id, 'msg': '添加成功！'}
        logger.info(f"({username} {res.get('msg')})")

        return JsonResponse(res)


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            if not user.is_active:
                res = {'code': 403, 'msg': '用户已禁用！'}
                return Response(res)
            token, created = Token.objects.get_or_create(user=user)
            # cache.set(token, True)    # token存入redis，EXPIRE设置过期时间
            # cache.client.expire(token, 3600)  # 过期时间设置为3600秒

            # request.session['user_id'] = user.id
            # request.session['username'] = user.username
            res = {
                'code': 200,
                'token': token.key,
                'user_id': user.id,
                'username': user.username,
                'msg': '认证成功'
            }
            logger.info(f"({res.get('username')} {res.get('msg')})")
        else:
            res = {'code': 500, 'msg': '用户名或密码错误！'}
            logger.info(f"({serializer.data.get('username')} {res.get('msg')})")

        return Response(res)


class ChangeUserPasswordView(APIView):

    @method_decorator(class_operation_log_decorator(
        model=User.objects,
        operation_type_id=OperationEnum.UPDATE,
        primary_key='user_id')
    )
    def put(self, request):
        username = request.data.get("username")
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get('confirm_password')
        try:
            user = User.objects.get(username=username)
        except:
            res = {'code': 500, 'msg': '用户不存在！'}
            return JsonResponse(res)
        if new_password != confirm_password:
            res = {'code': 500, 'msg': '两次密码不一致！'}
            return JsonResponse(res)
        if check_password(old_password, user.password):
            user.password = make_password(new_password)
            user.save()
            res = {'code': 200, 'user_id': user.id, 'msg': '修改成功！'}
        else:
            res = {'code': 500, 'msg': '原密码不正确！'}

        logger.info(f"({username} {res.get('msg')})")

        return JsonResponse(res)


# ******
@auth_service.permission(role=RoleEnum.ADMIN)
@def_operation_log_decorator(
    model=User.objects,
    operation_type_id=OperationEnum.UPDATE,
    primary_key='user_id',
    method='body'
)
def reset_password(request):
    """
    重置密码
    """
    data = json.loads(request.body)
    user_id = data.get('user_id')
    password = secret_util.get_random_password(6)
    encryt_password = make_password(password)

    User.objects.filter(id=user_id).update(password=encryt_password)

    res = {'code': 200, 'user_id': user_id,'password': password, 'msg': '重置成功！'}

    logger.info(f"({user_id} {res.get('msg')})")
    return JsonResponse(res)
