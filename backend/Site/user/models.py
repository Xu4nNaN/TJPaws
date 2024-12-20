from django.contrib.auth.models import User  # Django自带的用户模型
from django.db import models
from enum import Enum



class UserProfile(models.Model):
    USER_GENDER = (
        ('M', '男'),
        ('F', '女')
    )  # 性别选择，元组中的第一个元素是实际存储的值，第二个元素是在admin中显示的值

    # 一对一关联用户模型，用于扩展用户信息。原用户模型中的字段可以直接使用
    # 这里实际类似给user结构添加了一个扩展部分，user更像是外键，所以似乎这里有一些字段是冗余的
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='用户')

    name = models.CharField('昵称', max_length=50, default='TJPawer')
    gender = models.CharField('性别', max_length=1, choices=USER_GENDER, default='M')
    phone = models.CharField('手机号', max_length=11, blank=True, null=True)
    birthday = models.DateField('生日', blank=True, null=True)
    email = models.EmailField('邮箱', max_length=50, blank=True, null=True)
    avatar = models.ImageField('头像', upload_to="avatar/", default="avatar/default.jpg")
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)
    objects = models.Manager()
    role = models.CharField('角色', max_length=10,
                            choices=[('user','user'),('admin','admin'),('guest','guest')], default='user')
    is_banned = models.BooleanField('是否被封禁', default=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "user_profile"
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name  # 设置复数形式，即在admin中显示的名称会加一个s
        ordering = ["-create_time"]  # 按创建时间倒序排列