# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import AbstractUser
from certs_admin.enums.role_enum import RoleEnum


class MyUser(AbstractUser):
    role = models.IntegerField(default=RoleEnum.USER, verbose_name='用户权限')

    class Meta:
        verbose_name_plural = '用户表'
