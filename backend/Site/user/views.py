from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from .models import UserProfile,User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
#from .utils import verify_email
from django.conf import settings
import requests
import base64
from notification.utils import create_notification
from rest_framework_simplejwt.tokens import RefreshToken
# Create your views here.

def get_user_info(code):
    # 微信小程序的AppID和AppSecret
    secret = base64.b64decode(settings.APPSECRET).decode("utf-8")
    code_url = settings.CODE_TO_SESSION.format(settings.APPID, secret, code)
    response = requests.get(code_url).json()
    #print(response)
    if response.get("session_key"):
        return response
    else:
        return None

@csrf_exempt # 用于APIFOX测试需要
def user_login(request):
    if request.method == "POST":
        # TODO 
        if not request.POST.get("code"):
            return JsonResponse({"message": "缺少参数"}, status=400)
        code=request.POST.get("code")
        user_info=get_user_info(code)
        if not user_info:
            return JsonResponse({"message": "登录失败：无效的code"}, status=401)
        username = user_info.get("openid")
        # username = request.POST.get("openid")
        #首次登录时自动注册
        if username is None:
            return JsonResponse({"message": "登录失败：无效的openid"}, status=401)
        user, created = User.objects.get_or_create(username=username)

        UserProfile.objects.get_or_create(user=user)

        if user is not None:
            login(request, user) # 调用contrib.auth的login方法，将用户信息保存在session中并返回给客户端
            # refresh = RefreshToken.for_user(user)
            return JsonResponse({"message": "登录成功","isAdmin": user.userprofile.role=="admin","isBanned":user.userprofile.is_banned}, status=200)
        else:
            return JsonResponse({"message": "登录失败"}, status=401)

    else:
        return JsonResponse({"message": "无效的请求方法。"}, status=400)


'''由于改用微信小程序登录，注册功能废弃
@csrf_exempt
def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email=username
        password = request.POST.get("password")
        name = request.POST.get("name")
        verification_code = request.POST.get("verification_code")
        if UserProfile.user.objects.filter(username=username).exists():
            return JsonResponse({"message": "邮箱已被使用，请选择其他邮箱。"}, status=400)
        elif verify_email(email,verification_code)==False:
            return JsonResponse({"message": "验证码错误"}, status=400)
        else:
            user=UserProfile.user.objects.create_user(
                username=username,
                password=password
            )
            user_profile = UserProfile.objects.create(
                user=user,
                name=name,
                email=email
            )
            return JsonResponse({"message": "用户注册成功。"}, status=200)
    else:
        return JsonResponse({"message": "无效的请求方法。"}, status=400)
'''


@csrf_exempt
#@login_required
def change_user_status(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"message": "用户未登录"}, status=401)

        # 检查是否为管理员
        if not request.user.userprofile.role == "admin":
            return JsonResponse({"message": "权限不足"}, status=403)

        # 获取封禁的目标用户和操作类型
        target_name = request.POST.get("username")
        action = request.POST.get("action")  # "ban" 或 "unban"

        if not target_name or action not in ["ban", "unban"]:
            return JsonResponse({"message": "参数错误"}, status=400)

        try:
            target = User.objects.get(username=target_name)
        except User.DoesNotExist:
            return JsonResponse({"message": "用户不存在"}, status=404)

        target_profile = target.userprofile
        if target_profile.role == "admin":
            return JsonResponse({"message": "无法对管理员进行操作"}, status=403)

        if action == "ban":
            target_profile.is_banned = True
            target_profile.save()
            create_notification(target, "system", "您的账户已被封禁",0)
            return JsonResponse({"message": f"用户 {target_name} 已被封禁"}, status=200)

        elif action == "unban":
            target_profile.is_banned = False
            target_profile.save()
            create_notification(target, "system", "您的账户已被解除封禁",0)
            return JsonResponse({"message": f"用户 {target_name} 已被解除封禁"}, status=200)

    else:
        return JsonResponse({"message": "无效的请求方法。"}, status=400)


#功能需求
#管理员可以将普通账户拉入管理员团队中
@csrf_exempt
#@login_required
def add_admin(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"message": "用户未登录"}, status=401)

        # 检查是否为管理员
        if not request.user.userprofile.role == "admin":
            return JsonResponse({"message": "权限不足"}, status=403)


        target_name = request.POST.get("username")

        try:
            target = User.objects.get(username=target_name)
        except User.DoesNotExist:
            return JsonResponse({"message": "用户不存在"}, status=404)

        target_profile = target.userprofile

        target_profile.role = 'admin'
        target_profile.save()
        return JsonResponse({"message": f"用户 {target_name} 已被添加为管理员"}, status=200)

    else:
        return JsonResponse({"message": "无效的请求方法。"}, status=400)

@csrf_exempt
def get_userprofile(request):
    if request.method == "GET":
        username = request.GET.get("username")
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({"message": "用户不存在"}, status=404)
        user_profile = user.userprofile
        data = {
            "name": user_profile.name,
            "gender": user_profile.gender,
            "phone": user_profile.phone,
            "birthday": user_profile.birthday,
            "email": user_profile.email,
            "avatar": user_profile.avatar.url,
            "role": user_profile.role,
            "is_banned": user_profile.is_banned,
        }
        return JsonResponse({"message": "查询成功", "data": data}, status=200)
    else:
        return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
#@login_required
def upload_avatar(request):
    if request.method == "POST":
        avatar = request.FILES.get("file")
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({"message": "用户未登录"}, status=401)
        user_profile = user.userprofile
        user_profile.avatar = avatar
        user_profile.save()
        return JsonResponse({"message": "上传成功"}, status=200)
    return JsonResponse({"message": "无效的请求方法"}, status=400)

@csrf_exempt
#@login_required
def update_profile(request):
    if request.method == "POST":
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({"message": "用户未登录"}, status=401)
        name = request.POST.get("name")
        gender = request.POST.get("gender")
        phone = request.POST.get("phone")
        birthday = request.POST.get("birthday")
        email = request.POST.get("email")
        user_profile = user.userprofile
        if name:
            user_profile.name =name
        if gender:
            user_profile.gender =gender
        if phone:
            user_profile.phone =phone
        if birthday:
            user_profile.birthday =birthday
        if email:
            user_profile.email =email
        user_profile.save()
        return JsonResponse({"message": "修改成功"}, status=200)
    return JsonResponse({"message": "无效的请求方法"}, status=400)

@csrf_exempt
def get_my_profile(request):
    if request.method == "GET":
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({"message": "用户未登录"}, status=401)
        user_profile = user.userprofile
        data = {
            "name": user_profile.name,
            "gender": user_profile.gender,
            "phone": user_profile.phone,
            "birthday": user_profile.birthday,
            "email": user_profile.email,
            "avatar": user_profile.avatar.url,
            "role": user_profile.role,
            "is_banned": user_profile.is_banned,
        }
        return JsonResponse({"message": "查询成功", "data": data}, status=200)
    else:
        return JsonResponse({"message": "无效的请求方法"}, status=400)

@csrf_exempt
def upgrade_to_admin_with_key(request):
    if request.method == "POST":
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({"message": "用户未登录"}, status=401)
        key = request.POST.get("key")
        if key == '':
            user_profile = user.userprofile
            user_profile.role = 'admin'
            user_profile.save()
            return JsonResponse({"message": "升级成功"}, status=200)
        else:
            return JsonResponse({"message": "升级码错误"}, status=400)
    return JsonResponse({"message": "无效的请求方法"}, status=400)

