from django.db import models

class BaseModel(models.Model):
    '''模型抽象基类'''
    is_deleted = models.BooleanField('是否删除', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    @staticmethod
    def seek():
        return {}

    class Meta:
        abstract = True
        ordering = ['-id']
