# -*- coding: utf-8 -*-

from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps


class Envs(models.Model):
    name = models.CharField(unique=True, max_length=50, verbose_name="分组名称")
    en_name = models.CharField(blank=True, null=True, max_length=50, verbose_name="英文名称")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now_add=True, verbose_name="更新时间")
    comment = models.TextField(blank=True, null=True, verbose_name="备注")

    class Meta:
        db_table = "tb_envs"
        verbose_name_plural = "分组名称"
        ordering = ('-id',)


@receiver(post_migrate)
def add_default_envs(sender, **kwargs):
    """
    添加默认分组
    """
    if not apps.ready:  # 确保只在应用初次迁移后执行
        return
    try:
        Envs.objects.get(name='默认')
    except Envs.DoesNotExist:
        Envs.objects.create(name='默认', en_name='Default', comment='默认分组')
