from django.db import models
from django.utils import timezone


class User(models.Model):
    name = models.CharField(max_length=255, verbose_name='用户名')
    age = models.IntegerField(null=True, verbose_name='年龄')
    remark = models.TextField(null=True, verbose_name='备注描述')
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')
    created_time = models.DateTimeField(default=timezone.now, verbose_name='创建日期')
    relation_user = models.ForeignKey('User', null=True, on_delete=models.SET_NULL, verbose_name='关联的人')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "用户"
