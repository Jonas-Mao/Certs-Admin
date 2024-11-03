from django.contrib import admin


# 将扩展后的User表注册到Django Admin管理后台

from .models import MyUser

admin.site.register(MyUser)
