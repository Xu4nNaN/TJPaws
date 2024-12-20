from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ("like", "点赞"),
        ("comment", "评论"),
        ("animal_update", "动物资料更新"),
        ("report_result", "举报结果"),
        ("appeal_result", "Appeal Result"),
        ("feedback", "反馈"),
        ("feedback_result", "反馈结果"),
        ("system", "系统通知"),
    ]
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    content = models.TextField()
    related_id = models.IntegerField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
