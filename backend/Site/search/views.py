import json

from django.shortcuts import render
from django.http import JsonResponse
from material.models import Animal
from django.core.exceptions import FieldDoesNotExist
from django.db.models import CharField, TextField, IntegerField, \
    PositiveIntegerField, PositiveSmallIntegerField, SmallIntegerField, BigIntegerField
import math
from itertools import chain
# Create your views here.

def search_animals_by_integer(request):
    if request.method == "GET":
        query = request.GET.get("query",'')
        attribute = request.GET.get("attribute",'')
        if query == '' or attribute == '':
            return JsonResponse({"message": "缺少参数"}, status=400)
        if not query.isdigit():
            return JsonResponse({"message": "查询参数错误"}, status=400)
        try:
            query = int(query)  # 如果 query 不是整数，抛出异常
        except ValueError:
            return JsonResponse({"message": f"属性 {attribute} 需要一个有效的整数值"}, status=400)
        try:
            field=Animal._meta.get_field(attribute)
        except FieldDoesNotExist:
            return JsonResponse({"message": f"查询属性错误，Animal没有属性{attribute}"}, status=400)
        if not isinstance(field, (IntegerField,PositiveIntegerField,\
                                  PositiveSmallIntegerField,SmallIntegerField,BigIntegerField)):
            return JsonResponse({"message": f"查询属性错误，Animal属性{attribute}不是整数属性"}, status=400)
        animals = Animal.objects.filter(**{attribute: query})
        data = list(animals.values())
        return JsonResponse({"message": "查询成功", "data": data}, status=200)
    else:
        return JsonResponse({"message": "无效的请求方法"}, status=400)


def search_animals_by_string(request):
    if request.method == "GET":
        query = request.GET.get("query",'')
        attribute = request.GET.get("attribute",'')
        mode = request.GET.get("mode",'')
        if query == '' or attribute == '':
            return JsonResponse({"message": "缺少参数"}, status=400)
        if mode not in ['accurate', 'fuzzy']:
            return JsonResponse({"message": "查询模式错误"}, status=400)
        try:
            field=Animal._meta.get_field(attribute)
        except FieldDoesNotExist:
            return JsonResponse({"message": f"查询属性错误,Animal没有属性{attribute}"}, status=400)
        if not isinstance(field, (CharField, TextField)):
            return JsonResponse({"message": f"查询属性错误，Animal属性{attribute}不是字符串属性"}, status=400)
        # if attribute not in['nickname', 'species', 'breed']:
        #     return JsonResponse({"message": "查询属性错误"}, status=400)
        if mode == 'accurate':
            animals = Animal.objects.filter(**{attribute: query})
            data = list(animals.values())
        else:
            # 完全匹配
            exact_matches = Animal.objects.filter(**{attribute + '__iexact': query})

            # 包含匹配
            contains_matches = Animal.objects.filter(**{attribute + '__icontains': query})

            # 交叉部分匹配
            cross_matches = []
            for length in range(len(query), 0, -1):  # 按长度从长到短遍历
                for i in range(len(query) - length + 1):  # 内层循环通过开始位置生成子串
                    cross_query = query[i:i + length]
                    cross_matches.append(cross_query)

            # 获取交叉匹配的查询结果
            cross_query_results = Animal.objects.none()  # 初始化为空的 QuerySet
            for cross_query in cross_matches:
                cross_query_results |= Animal.objects.filter(**{attribute + '__icontains': cross_query})  # 使用 |= 进行合并

            # 合并结果，去重，且exact优先，然后是contains，最后是cross
            # animals = list(chain(exact_matches, contains_matches, cross_query_results))
            # #data = list(animals.values())#list没有values方法
            # data = []
            data=list(exact_matches.values())
            for animal in list(contains_matches.values()):
                if animal not in data:
                    data.append(animal)
            for animal in list(cross_query_results.values()):
                if animal not in data:
                    data.append(animal)


        # 转换为字典列表

        return JsonResponse({"message": "查询成功", "data": data}, status=200)
    else:
        return JsonResponse({"message": "无效的请求方法"}, status=400)


def search_animals_by_distance(request):
    def haversine(lat1, lon1, lat2, lon2):
        # 将角度转换为弧度
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        R = 6371.01  # 地球平均半径，单位为公里
        # 纬度差和经度差
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        # Haversine 公式
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        # 计算距离
        distance = R * c
        return distance

    if request.method == "GET":
        latitude = request.GET.get("latitude",'')
        longitude = request.GET.get("longitude",'')
        distance = request.GET.get("distance",'')
        if latitude == '' or longitude == '' or distance == '':
            return JsonResponse({"message": "缺少参数"}, status=400)
        if (not latitude.replace('.', '', 1).isdigit() or
                not longitude.replace('.', '', 1).isdigit() or not distance.replace('.', '', 1).isdigit()):
            return JsonResponse({"message": "查询参数错误"}, status=400)
        latitude = float(latitude)
        longitude = float(longitude)
        distance = float(distance)
        animals = Animal.objects.all()
        data = []
        for animal in animals:
            # 获取动物位置并解析 JSON
            location = json.loads(animal.location) if animal.location else None

            # 如果 location 不为空，则计算距离
            if location:
                try:
                    lat = float(location['latitude'])
                    lon = float(location['longitude'])
                except (ValueError, KeyError):
                    lat=0
                    lon=0

                # 计算距离
                if haversine(latitude, longitude, lat, lon) <= distance:
                    # 将动物ID和位置一并返回
                    data.append({
                        'id': animal.id,
                        'location': location,
                        'animal_name': animal.nickname,
                    })
        return JsonResponse({"message": "查询成功", "data": data}, status=200)

    else:
        return JsonResponse({"message": "无效的请求方法"}, status=400)
