from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
# Register your models here.
from django.contrib.auth.models import User

from .models import UserProfile

admin.site.unregister(User)  # 取消注册原User模型，避免冲突


class UserProfileInline(admin.StackedInline):  # 定义一个内联类，用于在用户管理页面嵌入用户信息
    model = UserProfile
    can_delete = False
    verbose_name_plural = '用户信息'


class UserProfileAdmin(UserAdmin):  # 定义一个用户管理类，用于自定义用户管理页面
    inlines = (UserProfileInline,)  # 将内联类添加到用户管理页面
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')  # 定义用户列表显示的字段
    list_filter = ('is_staff', 'is_active')  # 定义用户列表的过滤器
    search_fields = ('username', 'email', 'first_name', 'last_name')  # 定义用户列表的搜索字段
    fieldsets = (  # 定义用户信息编辑页面的字段分组
        (None, {'fields': ('username', 'password')}),
        ('个人信息', {'fields': ('first_name', 'last_name', 'email')}),
        ('权限', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('时间节点', {'fields': ('last_login', 'date_joined')}),
    )


admin.site.register(User, UserProfileAdmin)  # 重新注册User模型和自定义的用户管理类
