from django.shortcuts import render
from .models import Notification
from django.http import JsonResponse
from django.contrib.auth.models import User
from .utils import create_notification
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
# Create your views here.


#管理员向用户发送通知
@csrf_exempt
#@login_required
def send_notification(request):
    if request.method == "POST":
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({"message": "用户未登录"}, status=401)
        if not user.userprofile.role == "admin":
            return JsonResponse({"message": "权限不足"}, status=403)
        receivers_id = request.POST.get("receivers_id")
        notification_type = 'system'
        content = request.POST.get("content")
        if not receivers_id or not content:
            return JsonResponse({"message": "缺少参数"}, status=400)
        if receivers_id== 'all':
            receivers = User.objects.all()
        else:
            receivers_id = receivers_id.split(',')
            receivers = User.objects.filter(id__in=receivers_id)
        for receiver in receivers:
            create_notification(receiver, notification_type, content,0)
        return JsonResponse({"message": "通知发送成功"}, status=200)
    else:
        return JsonResponse({"message": "无效的请求方法"}, status=400)

#用户查看通知
@csrf_exempt
#@login_required
def get_notifications(request):
    if request.method == "GET":
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({"message": "用户未登录"}, status=401)
        notifications = user.notifications.all()
        data = []
        for notification in notifications:
            data.append({
                "notification_id": notification.id,
                "notification_type": notification.notification_type,
                "content": notification.content,
                "related_id": notification.related_id,
                "is_read": notification.is_read,
                "created_at": notification.created_at
            })
            notification.is_read = True
            notification.save()
        return JsonResponse({"message": "查询成功", "data": data}, status=200)
    else:
        return JsonResponse({"message": "无效的请求方法"}, status=400)


