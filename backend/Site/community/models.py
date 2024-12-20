from django.db import models
from django.contrib.auth.models import User


# Create your models here.

# 帖子和评论的类实现
class Like_Post(models.Model):
    #点赞用户
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    #点赞的帖子
    content = models.ForeignKey('Post', on_delete=models.CASCADE)
    class Meta:
        unique_together = ('user', 'content')

class Like_Comment(models.Model):
    #点赞用户
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    #点赞的评论
    content = models.ForeignKey('Comment', on_delete=models.CASCADE)
    class Meta:
        unique_together = ('user', 'content')

#基类Content
class Content(models.Model):
    #作者
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    #内容
    content = models.TextField()
    #创建时间
    created_time = models.DateTimeField(auto_now_add=True)
    #修改时间
    modified_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract= True

#帖子类
class Post(Content):
    #浏览数
    view = models.IntegerField(default=0)
    title = models.CharField(max_length=100)#标题

class Comment(Content):
    #评论的帖子
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    #评论的父评论
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.content

class Report(models.Model):
    OBJECT_TYPES = [
        ("post", "Post"),
        ("comment", "Comment"),
    ]
    target_type = models.CharField(max_length=20, choices=OBJECT_TYPES)
    target_id = models.IntegerField()
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports")
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="pending")
    admin_notes = models.TextField(blank=True,)
    finished_at = models.DateTimeField(null=True, blank=True)

