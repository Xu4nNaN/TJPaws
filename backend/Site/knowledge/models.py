from django.contrib.auth.models import User  # 假设需要记录作者
from django.db import models


class Article(models.Model):
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('published', '已发布'),
    ]

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name="状态")  # 文章状态
    title = models.CharField(max_length=255, verbose_name="标题")  # 文章标题
    content = models.TextField(verbose_name="内容")  # 文章正文
    categories = models.ManyToManyField('Category', related_name='articles', verbose_name="分类")  # 多对多关联分类
    tags = models.ManyToManyField('Tag', related_name='articles', verbose_name="标签")  # 多对多关联标签
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="作者")  # 文章作者
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")  # 创建时间
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")  # 更新时间
    cover_image = models.ImageField(upload_to='article_covers/', null=True, blank=True, verbose_name="封面图片")  # 封面图片
    media_resources = models.ManyToManyField('MediaResource', related_name='articles', verbose_name="媒体资源")  # 多对多关联媒体资源

    def __str__(self):
        return self.title


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="分类名称")  # 分类名称
    description = models.TextField(blank=True, null=True, verbose_name="分类描述")  # 分类描述
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="父分类")  # 支持分类层级

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="标签名称")  # 标签名称
    description = models.TextField(blank=True, null=True, verbose_name="标签描述")  # 标签描述

    def __str__(self):
        return self.name


class MediaResource(models.Model):
    RESOURCE_TYPES = [
        ('image', '图片'),
        ('video', '视频'),
    ]
    reference_name = models.CharField(max_length=50, unique=True, default="", verbose_name="引用名")  # 引用名
    file = models.FileField(upload_to='media_resources/', verbose_name="文件路径")  # 文件存储路径
    resource_type = models.CharField(max_length=10, choices=RESOURCE_TYPES, verbose_name="资源类型")  # 资源类型（图片/视频）
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name="资源描述")  # 描述
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="上传时间")  # 上传时间
    def __str__(self):
        return f"{self.reference_name} ({self.get_resource_type_display()})"


class Like(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='likes', verbose_name="文章")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="点赞时间")


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments', verbose_name="文章")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="用户", related_name='comments')
    content = models.TextField(verbose_name="评论内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="评论时间")


class ViewCount(models.Model):
    article = models.OneToOneField(Article, on_delete=models.CASCADE, related_name='view_count', verbose_name="文章")
    count = models.PositiveIntegerField(default=0, verbose_name="浏览次数")
