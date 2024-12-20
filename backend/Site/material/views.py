import json
import urllib.parse
from django.contrib.auth.decorators import login_required
# from django.contrib.gis.geos import Point
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from notification.utils import create_notification
from .models import Animal, Feedback, AnimalImage, AnimalLeaderBoard, Like_Animal
import warnings

"""
动物资料处理部分
"""


# TODO 测试中，所有admin的判断都是相反的！记得改回来！

def get_animal_in_request_deprecation(request):
    warnings.warn("It is deprecated", DeprecationWarning)
    if request.method == 'POST':
        nickname = request.POST.get("nickname")
        species = request.POST.get("species")
        breed = request.POST.get("breed")
        origin_thumbnail = request.POST.get("origin_thumbnail")
        new_thumbnail = request.FILES.get("new_thumbnail")
        origin_images = request.POST.getlist("origin_images")
        new_images = request.FILES.getlist("new_images")
        description = request.POST.get("description")
        location_lat = request.POST.get("latitude")
        location_lon = request.POST.get("longitude")
        notes = request.POST.get("notes")
    else:
        # 处理其他请求方法
        return None, None, None, None, None, None, None, None, None, None, None

    return nickname, species, breed, origin_thumbnail, new_thumbnail, origin_images, new_images, description, location_lat, location_lon, notes


@csrf_exempt
# 发布动物资料
def create_animal(request):
    warnings.warn("It is deprecated", DeprecationWarning)
    if not request.user.is_authenticated:
        return JsonResponse({"message": "用户未登录"}, status=401)
    if request.user.userprofile.role != 'admin':
        return JsonResponse({"message": "无权操作"}, status=403)
    if request.method == "POST":
        # 获取 POST 请求数据
        nickname, species, breed, origin_thumbnail, new_thumbnail, origin_images, new_images, description, location_lat, location_lon, notes = get_animal_in_request_deprecation(
            request)

        # 验证必填字段
        if not nickname or not species:
            return JsonResponse({"message": "昵称和种类为必填项。"}, status=400)

        # location = Point(float(location_lon), float(location_lat))  # TODO 创建 Point 对象
        # 将location按照经纬度的形式存储为json
        location = json.dumps({"latitude": location_lat, "longitude": location_lon})
        animal = Animal.objects.create(
            nickname=nickname,
            species=species,
            breed=breed,
            description=description,
            location=location,
            notes=notes,
        )

        # 同时创建动物排行榜
        AnimalLeaderBoard.objects.create(animal=animal, score=0)

        if new_thumbnail:
            animal_image = AnimalImage.objects.create(animal=animal, image=new_thumbnail)
            animal.thumbnail = animal_image
            animal.save()
        # 处理上传的多个图片
        ImageCounts = AnimalImage.objects.filter(animal=animal).count()
        for image in new_images:
            AnimalImage.objects.create(animal=animal, image=image, order=ImageCounts)
            ImageCounts += 1

        return JsonResponse({"message": "动物资料创建成功。"}, status=201)
    return JsonResponse({"message": "无效的请求方法。"}, status=400)


@csrf_exempt
def update_animal(request, animal_id):
    warnings.warn("It is deprecated", DeprecationWarning)
    if not request.user.is_authenticated:
        return JsonResponse({"message": "用户未登录"}, status=401)
    if request.user.userprofile.role != 'admin':
        return JsonResponse({"message": "无权操作"}, status=403)
    try:
        animal = Animal.objects.get(id=animal_id)
    except Animal.DoesNotExist:
        return JsonResponse({"message": "动物资料未找到"}, status=404)

    if request.user.userprofile.role != 'admin':
        return JsonResponse({"message": "无权操作"}, status=403)

    if request.method == "POST":
        nickname, species, breed, origin_thumbnail, new_thumbnail, origin_images, new_images, description, location_lat, location_lon, notes = get_animal_in_request_deprecation(
            request)

        # 验证地理位置信息
        if location_lat and location_lon:
            # TODO 暂时放弃
            # location = Point(float(location_lon), float(location_lat))
            location = json.dumps({"latitude": location_lat, "longitude": location_lon})
        else:
            location = animal.location  # 如果没有提供位置，保留原位置信息

        # 对origin_thumbnail和origin_images的每一项去除前缀/media/
        if origin_thumbnail:
            origin_thumbnail = urllib.parse.unquote(origin_thumbnail[7:])
        if origin_images:
            origin_images = [urllib.parse.unquote(image[7:]) for image in origin_images]

        # 更新部分字段
        if nickname is not None:
            animal.nickname = nickname
        if species is not None:
            animal.species = species
        if breed is not None:
            animal.breed = breed
        if origin_thumbnail:
            thumbnail = AnimalImage.objects.get(image=origin_thumbnail)  # TODO:不确定是否有问题
            animal.thumbnail = thumbnail
        if new_thumbnail:
            animal_image = AnimalImage.objects.create(animal=animal, image=new_thumbnail)
            animal.thumbnail = animal_image
        if description is not None:
            animal.description = description
        if location != animal.location:
            animal.location = location
        if notes is not None:
            animal.notes = notes
        animal.save()

        image_order = 0
        if origin_images:
            current_images = set(animal.images.values_list('image', flat=True))  # 获取当前动物的所有图片
            # 更新匹配到的图片顺序
            for image_path in origin_images:
                if image_path in current_images:
                    animal_image = AnimalImage.objects.get(image=image_path)  # TODO:不确定是否有问题
                    animal_image.order = image_order
                    image_order += 1
                    animal_image.save()
                    current_images.remove(image_path)  # 从当前图片集合中移除已匹配的图片
                    print(image_path)
            AnimalImage.objects.filter(animal=animal, image__in=current_images).delete()  # 删除没有匹配到的图片记录
        if new_images:
            for image in new_images:
                AnimalImage.objects.create(animal=animal, image=image, order=image_order)
                image_order += 1

        return JsonResponse({"message": "动物资料更新成功。"}, status=200)
    return JsonResponse({"message": "无效的请求方法。"}, status=400)


@csrf_exempt
def delete_animal(request, animal_id):
    if not request.user.is_authenticated:
        return JsonResponse({"message": "用户未登录"}, status=401)
    if request.user.userprofile.role != 'admin':
        return JsonResponse({"message": "无权操作"}, status=403)
    if request.method == "DELETE":
        try:
            animal = Animal.objects.get(id=animal_id)
        except Animal.DoesNotExist:
            return JsonResponse({"message": "动物资料未找到"}, status=404)
        animal.delete()
        return JsonResponse({"message": "动物资料删除成功。"}, status=200)
    return JsonResponse({"message": "无效的请求方法。"}, status=400)


def animal_info_handle(animal):
    animal_images = AnimalImage.objects.filter(animal=animal)
    # 将动物资料转化为 JSON 格式
    animal_data = {
        "id": animal.id,
        "nickname": animal.nickname,
        "species": animal.species,
        "breed": animal.breed,
        "thumbnail": animal.thumbnail.image.url if animal.thumbnail else None,
        "images": [animal_image.image.url for animal_image in animal_images],  # TODO 返回的是图片的路径
        "description": animal.description,
        "location": {
            "latitude": 162,
            "longitude": 133
        },
        "notes": animal.notes
    }

    # 解析 animal.location 并设置 latitude 和 longitude
    if animal.location:
        try:
            location_dict = json.loads(animal.location)
            animal_data["location"]["latitude"] = location_dict.get("latitude")
            animal_data["location"]["longitude"] = location_dict.get("longitude")
        except json.JSONDecodeError:
            # TODO 处理解析错误
            pass
    return animal_data


@csrf_exempt
def get_animal(request, animal_id):
    try:  # 获取指定 ID 的动物资料
        animal = Animal.objects.get(id=animal_id)
    except Animal.DoesNotExist:
        return JsonResponse({"message": "动物资料未找到"}, status=404)

    animal_data = animal_info_handle(animal)
    user = request.user
    if user.is_authenticated:
        liked = Like_Animal.objects.filter(user=user, animal=animal).exists()
    else:
        liked = False
    animal_data["liked"] = liked
    # 返回 JSON 格式的动物资料
    return JsonResponse(animal_data, status=200)


@csrf_exempt
def get_animals(request):
    total_animals = 0
    if request.method == 'GET':
        begin = request.GET.get('begin', 0)  # 默认从第 0 条记录开始
        amount = request.GET.get('amount', 10)  # 默认获取 10 条记录
        try:
            begin = int(begin)
            amount = int(amount)
            if amount <= 0 or begin < 0:
                return JsonResponse({"message": "无效的数量"}, status=400)
        except ValueError:
            return JsonResponse({"message": "数量必须是整数"}, status=400)
        animal_list = []

        for id in range(begin, begin + amount):  # TODO 上限可能不足
            try:  # 获取指定 ID 的动物资料
                animal = Animal.objects.get(id=id)
                total_animals = Animal.objects.count()
            except Animal.DoesNotExist:
                continue
            animal_data = animal_info_handle(animal)
            animal_list.append(animal_data)

        return JsonResponse({"animals": animal_list, "total_animals": total_animals}, status=200)
    else:
        return JsonResponse({"message": "不支持的方法"}, status=405)


"""
动物资料反馈部分
"""


@csrf_exempt
def submit_feedback(request, animal_id):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"message": "用户未登录"}, status=401)
        try:
            animal = Animal.objects.get(id=animal_id)
        except Animal.DoesNotExist:
            return JsonResponse({"message": "动物资料未找到"}, status=404)

        suggested_changes = request.POST.get("suggested_changes", {})
        feedback_notes = request.POST.get("feedback_notes", "")

        if suggested_changes == "":
            return JsonResponse({"message": "反馈内容不能为空"}, status=400)

        # 创建反馈记录
        feedback = Feedback.objects.create(
            user=request.user,
            animal=animal,
            suggested_changes=suggested_changes,
            feedback_notes=feedback_notes
        )
        # 获取本人user结构用于通知
        # user = request.user
        # 生成通知
        # create_notification(user, "feedback", feedback.feedback_notes, feedback.id)

        return JsonResponse({"message": "反馈提交成功", "feedback_id": feedback.id}, status=201)
    return JsonResponse({"message": "无效的请求方法"}, status=400)


# @login_required
def get_feedbacks(request):
    if not request.user.is_authenticated:
        return JsonResponse({"message": "用户未登录"}, status=401)
    if request.user.userprofile.role == 'admin':  # 管理员获得未处理的反馈
        status = request.GET.get("status", "pending")  # 默认显示未处理的反馈
        feedbacks = Feedback.objects.all()
    else:  # 普通用户获得自己的反馈
        feedbacks = Feedback.objects.filter(user=request.user)

    feedback_list = [
        {
            "id": fb.id,
            "animal": fb.animal.nickname,
            "suggested_changes": fb.suggested_changes,
            "feedback_notes": fb.feedback_notes,
            "status": fb.status,
            "created_at": fb.created_at,
            "updated_at": fb.updated_at,
            "admin_notes": fb.admin_notes
        }
        for fb in feedbacks
    ]

    return JsonResponse({"feedbacks": feedback_list}, status=200)


@csrf_exempt
# @login_required
def update_feedback(request, feedback_id):
    if not request.user.is_authenticated:
        return JsonResponse({"message": "用户未登录"}, status=401)
    if request.user.userprofile.role != 'admin':
        return JsonResponse({"message": "无权操作"}, status=403)
    # 此处只是修改反馈的处理结果，具体资料的更新使用update_animal接口
    if request.method == "POST":
        try:
            feedback = Feedback.objects.get(id=feedback_id)
        except Feedback.DoesNotExist:
            return JsonResponse({"message": "反馈未找到"}, status=404)

        feedback.status = request.POST.get("status", feedback.status)
        feedback.admin_notes = request.POST.get("admin_notes", feedback.admin_notes)
        feedback.save()
        # 生成通知
        create_notification(feedback.user, "system",  f"您的反馈已被处理，处理结果：{feedback.admin_notes}", feedback.id)
        return JsonResponse({"message": "反馈更新成功"}, status=200)
    return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
def get_animal_leaderboard(request):
    if request.method == 'GET':
        leaderboards = AnimalLeaderBoard.objects.all()
        rank = 1
        leaderboard_list = []
        for lb in leaderboards:
            animal_data = {
                "rank": rank,
                "animal_id": lb.animal.id,
                "nickname": lb.animal.nickname,
                "score": lb.score,
                "updated_at": lb.updated_at
            }
            leaderboard_list.append(animal_data)
            rank += 1
        return JsonResponse({"leaderboard": leaderboard_list}, status=200)
    else:
        return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
# @login_required
def set_animal_score(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({"message": "用户未登录"}, status=401)
        if request.user.userprofile.role != 'admin':
            return JsonResponse({"message": "无权操作"}, status=403)
        animal_id = request.POST.get("animal_id")
        score = request.POST.get("score")
        if not animal_id or not score:
            return JsonResponse({"message": "缺少参数"}, status=400)
        try:
            score = int(score)
        except ValueError:
            return JsonResponse({"message": "分数必须是整数"}, status=400)
        try:
            animal = Animal.objects.get(id=animal_id)
        except Animal.DoesNotExist:
            return JsonResponse({"message": "没有该动物"}, status=404)
        animal.animalleaderboard.set_score(score)
        return JsonResponse({"message": "设置成功"}, status=200)
    else:
        return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
# @login_required
def like_animal_switch(request):
    if request.method == 'POST':
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({"message": "用户未登录"}, status=401)
        animal_id = request.POST.get("animal_id")
        if not animal_id:
            return JsonResponse({"message": "缺少参数"}, status=400)
        try:
            animal = Animal.objects.get(id=animal_id)
        except Animal.DoesNotExist:
            return JsonResponse({"message": "没有该动物"}, status=404)
        like, created = Like_Animal.objects.get_or_create(user=user, animal=animal)
        if not created:
            like.delete()
            return JsonResponse({"message": "取消点赞成功"}, status=201)
        return JsonResponse({"message": "点赞成功"}, status=200)
    else:
        return JsonResponse({"message": "无效的请求方法"}, status=400)


def get_animal_in_request(request):
    if request.method == 'POST':
        nickname = request.POST.get("nickname")
        species = request.POST.get("species")
        breed = request.POST.get("breed")
        description = request.POST.get("description")
        location_lat = request.POST.get("latitude")
        location_lon = request.POST.get("longitude")
    else:  # 处理其他请求方法
        return None, None, None, None, None, None, None
    return nickname, species, breed, description, location_lat, location_lon


@csrf_exempt
# 发布动物资料
def publish_animal(request):
    if not request.user.is_authenticated:
        return JsonResponse({"message": "用户未登录"}, status=401)
    if request.user.is_authenticated and request.user.userprofile.role != 'admin':
        return JsonResponse({"message": "无权操作"}, status=403)
    if request.method == "POST":
        # 获取 POST 请求数据
        nickname, species, breed, description, location_lat, location_lon = get_animal_in_request(request)
        # 验证必填字段
        if not nickname or not species:
            return JsonResponse({"message": "昵称和种类为必填项。"}, status=400)
        # 将location按照经纬度的形式存储为json
        location = json.dumps({"latitude": location_lat, "longitude": location_lon})
        animal = Animal.objects.create(
            nickname=nickname,
            species=species,
            breed=breed,
            description=description,
            location=location,
        )

        # 同时创建动物排行榜
        AnimalLeaderBoard.objects.create(animal=animal, score=0)

        return JsonResponse({"message": "动物资料创建成功。", "id": animal.id}, status=201)
    return JsonResponse({"message": "无效的请求方法。"}, status=400)


@csrf_exempt
def upload_medium(request):
    if not request.user.is_authenticated:
        return JsonResponse({"message": "用户未登录"}, status=401)
    if request.user.is_authenticated and request.user.userprofile.role != 'admin':
        return JsonResponse({"message": "无权操作"}, status=403)
    if request.method == "POST":
        animal_id = request.POST.get("animal_id")
        file = request.FILES.get("file")
        file_name = request.POST.get("file_name")
        order = request.POST.get("order")

        # 校验
        if not file or not file_name:
            return JsonResponse({"message": "缺少必要参数"}, status=400)

        try:
            order = int(order)
            animal_id = int(animal_id)
        except ValueError:
            return JsonResponse({"message": "排序必须是整数"}, status=400)

        try:
            animal = Animal.objects.get(id=animal_id)
        except Animal.DoesNotExist:
            return JsonResponse({"message": "没有该动物"}, status=404)

        # Create AnimalImage object
        animal_image = AnimalImage.objects.create(
            animal=animal,
            image=file,
            order=order,
            description=animal.nickname + " " + file_name
        )

        # 当order为1时，更新thumbnail
        if order == 1:
            try:
                animal.thumbnail = animal_image
                animal.save()
            except AnimalImage.DoesNotExist:
                return JsonResponse({"message": "没有该动物"}, status=404)

        return JsonResponse({"message": "上传成功"}, status=201)
    return JsonResponse({"message": "无效的请求方法"}, status=400)
