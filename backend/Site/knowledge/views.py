import re
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Article, Category, Tag, MediaResource, Like, Comment
import os
from PIL import Image
import base64
from io import BytesIO
import warnings


# TODO 测试中，所有admin的判断都是相反的！记得改回来！

@csrf_exempt
def create_article(request):
    warnings.warn("It is deprecated", DeprecationWarning)
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"message": "用户未登录"}, status=401)
        if request.user.userprofile.role != 'admin':  # 检查是否为管理员
            return JsonResponse({"message": "无权限操作"}, status=403)

        # 从表单中获取数据
        title = request.POST.get("title")
        content = request.POST.get("content")
        category_names = request.POST.getlist("categories")  # 分类名称列表
        tag_names = request.POST.getlist("tags")  # 标签名称列表
        status = request.POST.get("status", "draft")  # 默认保存为草稿
        cover_image = request.FILES.get("cover_image")  # 封面图片

        # 验证输入字段
        if not title or not content:
            return JsonResponse({"message": "标题和内容为必填项"}, status=400)

        # 创建文章实例
        article = Article.objects.create(
            title=title,
            content=content,
            author=request.user,
            status=status,
            cover_image=cover_image
        )

        if category_names:
            categories = Category.objects.filter(name__in=category_names)
            article.categories.set(categories)

        if tag_names:
            tags = []
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name)  # get_or_create()方法返回一个元组，第一个元素是对象，第二个元素是一个布尔值，指示对象是否是新创建的
                tags.append(tag)
            article.tags.set(tags)

        return JsonResponse({"message": "文章创建成功", "article_id": article.id}, status=201)

    return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
def upload_media(request):
    warnings.warn("It is deprecated", DeprecationWarning)
    if not request.user.is_authenticated:
        return JsonResponse({"message": "用户未登录"}, status=401)
    if request.user.userprofile.role != 'admin':
        return JsonResponse({"message": "无权操作"}, status=403)
    if request.method == "POST":
        resource_file = request.FILES.get("file")
        reference_name = request.POST.get("reference_name")
        resource_type = request.POST.get("resource_type")
        description = request.POST.get("description")

        # 校验
        if not resource_file or not reference_name or not resource_type:
            return JsonResponse({"message": "缺少必要参数"}, status=400)
        if MediaResource.objects.filter(reference_name=reference_name).exists():
            return JsonResponse({"message": "引用名已存在，请换一个名字"}, status=400)

        # 保存资源
        resource = MediaResource.objects.create(
            file=resource_file,
            reference_name=reference_name,
            resource_type=resource_type,
            description=description
        )
        return JsonResponse({"message": "资源上传成功", "url": resource.file.url}, status=201)

    return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
def get_all_media(request):
    if not request.user.is_authenticated:
        return JsonResponse({"message": "用户未登录"}, status=401)
    warnings.warn("It is deprecated", DeprecationWarning)
    if request.method == "GET":
        media_list = []
        media_resources = MediaResource.objects.all()
        for media in media_resources:
            # associated_article = media.article
            # associated_title = associated_article.title if associated_article else None

            media_list.append({
                "reference_name": media.reference_name,
                "resource_type": media.resource_type,
                "uploaded_at": media.uploaded_at,
                # "associated_articles": associated_title
                "url": media.file.url
            })

        return JsonResponse({"media": media_list}, status=200)
    else:
        return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
def get_thumbnails(request):
    if not request.user.is_authenticated:
        return JsonResponse({"message": "用户未登录"}, status=401)
    warnings.warn("It is deprecated", DeprecationWarning)
    if request.method == "GET":
        media_resources = MediaResource.objects.filter(resource_type='image')
        thumbnails = []

        for media in media_resources:
            try:
                # 打开图片文件
                with Image.open(media.file.path) as img:
                    # 生成缩略图
                    img.thumbnail((100, 100))  # 设定缩略图大小
                    buffer = BytesIO()
                    img.save(buffer, format="JPEG")
                    thumbnail_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                    thumbnails.append({
                        "reference_name": media.reference_name,
                        "thumbnail": thumbnail_base64
                    })
            except Exception as e:
                return JsonResponse({"message": f"生成缩略图失败: {str(e)}"}, status=500)

        return JsonResponse({"thumbnails": thumbnails}, status=200)
    else:
        return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
def download_media(request, reference_name):
    if not request.user.is_authenticated:
        return JsonResponse({"message": "用户未登录"}, status=401)
    warnings.warn("It is deprecated", DeprecationWarning)
    if request.method == "GET":
        try:
            media = MediaResource.objects.get(reference_name=reference_name)
            media_file_path = media.file.path  # 获取文件的路径

            if os.path.exists(media_file_path):
                return FileResponse(open(media_file_path, 'rb'), content_type="application/octet-stream")
            else:
                return JsonResponse({"message": "媒体资源文件不存在"}, status=404)
        except MediaResource.DoesNotExist:
            return JsonResponse({"message": "媒体资源不存在"}, status=404)
    else:
        return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
def get_media(request, reference_name):
    if not request.user.is_authenticated:
        return JsonResponse({"message": "用户未登录"}, status=401)
    warnings.warn("It is deprecated", DeprecationWarning)
    if request.method == "GET":
        try:
            media = MediaResource.objects.get(reference_name=reference_name)
            media_file_url = media.file.url  # 获取文件的URL

            return JsonResponse({"url": media_file_url}, status=200)
        except MediaResource.DoesNotExist:
            return JsonResponse({"message": "媒体资源不存在"}, status=404)
    else:
        return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
def delete_media(request, reference_name):
    warnings.warn("It is deprecated", DeprecationWarning)
    if not request.user.is_authenticated:
        return JsonResponse({"message": "用户未登录"}, status=401)
    if request.user.userprofile.role != 'admin':
        return JsonResponse({"message": "无权操作"}, status=403)
    if request.method == "DELETE":
        try:
            media = MediaResource.objects.get(reference_name=reference_name)
            # 删除文件本身 # TODO 需要确定开放情况
            # media_file_path = media.file.path
            # if os.path.exists(media_file_path):
            #     os.remove(media_file_path)
            # 删除数据库记录
            media.delete()
            return JsonResponse({"message": "媒体资源已删除"}, status=200)
        except MediaResource.DoesNotExist:
            return JsonResponse({"message": "媒体资源不存在"}, status=404)
    else:
        return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
def get_articles(request):
    if request.method == "GET":
        begin = int(request.GET.get("begin", 0))  # 起始位置，默认为 0
        amount = int(request.GET.get("amount", 10))  # 返回数量，默认为 10
        print(begin, amount)
        try:
            begin = int(begin)
            amount = int(amount)
            if begin < 0 or amount <= 0:
                return JsonResponse({"message": "无效的数量"}, status=400)
        except ValueError:
            return JsonResponse({"message": "数量必须是整数"}, status=400)

        # 获取已发布的文章并排序
        articles = Article.objects.filter(status="published").order_by("-updated_at")
        total_articles = articles.count()

        if begin >= total_articles:
            return JsonResponse({"message": "起始位置超出范围"}, status=404)

        # 获取指定范围的文章
        articles_slice = articles[begin:begin + amount]
        article_list = [
            {
                "id": article.id,
                "title": article.title,
                "summary": re.sub(r"!\[img]\(.*?\)", "", article.content)[:55] + ("..." if len(re.sub(r"!\[img]\(.*?\)", "", article.content)) > 55 else ""),
                "cover_image": article.cover_image.url if article.cover_image else None,
                "categories": [category.name for category in article.categories.all()],
            }
            for article in articles_slice
        ]

        return JsonResponse({"articles": article_list, "total_articles": total_articles, "begin": begin, "amount": len(article_list),
                             }, status=200)
    else:
        return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
def get_article_deprecation(request, article_id):
    warnings.warn("It is deprecated", DeprecationWarning)
    if request.method == "GET":
        try:
            if request.user.is_authenticated and request.user.userprofile.role != 'admin':
                article = Article.objects.get(id=article_id, status="published")
            else:
                article = Article.objects.get(id=article_id)

            # 替换文章内容中的图片标签
            def replace_media(match, flag):
                media_reference = match.group(1)
                try:
                    media = MediaResource.objects.get(reference_name=media_reference)
                    if flag == "image":
                        return f'<img src="{media.file.url}" alt="{media_reference}">'
                    elif flag == "video":
                        return f'<video src="{media.file.url}" controls></video>'
                    else:  # 处理audio
                        return f'<audio src="{media.file.url}" controls></audio>'
                except MediaResource.DoesNotExist:
                    return f'[内容丢失: {media_reference}]'

            pattern = r"!\[img\]\((.*?)\)"
            content_with_images = re.sub(pattern, lambda x: replace_media(x, "image"), article.content)
            pattern = r"!\[video\]\((.*?)\)"
            content_with_images = re.sub(pattern, lambda x: replace_media(x, "video"), content_with_images)
            pattern = r"!\[audio\]\((.*?)\)"
            content_with_images = re.sub(pattern, lambda x: replace_media(x, "audio"), content_with_images)

            article_detail = {
                "id": article.id,
                "title": article.title,
                "content": content_with_images,
                "time": article.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                "categories": [category.name for category in article.categories.all()],
                "tags": [tag.name for tag in article.tags.all()],
                "likes": article.likes.count(),
                "cover_image": article.cover_image.url if article.cover_image else None,
            }
            return JsonResponse(article_detail, status=200)
        except Article.DoesNotExist:
            return JsonResponse({"message": "文章不存在"}, status=404)
    else:
        return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
def update_article(request, article_id):
    warnings.warn("It is deprecated", DeprecationWarning)
    if not request.user.is_authenticated:
        return JsonResponse({"message": "用户未登录"}, status=401)
    if request.user.userprofile.role != 'admin':
        return JsonResponse({"message": "无权操作"}, status=403)
    if request.method == "POST":
        try:
            article = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            return JsonResponse({"message": "文章不存在"}, status=404)

        # 从表单中获取数据
        title = request.POST.get("title")
        content = request.POST.get("content")
        category_names = request.POST.getlist("categories")
        tag_names = request.POST.getlist("tags")
        status = request.POST.get("status")
        cover_image = request.FILES.get("cover_image")

        # 更新非空字段
        if title:
            article.title = title
        if content:
            article.content = content
        if status:
            article.status = status
        if cover_image:
            article.cover_image = cover_image

        if category_names:
            article.categories.clear()
            categories = Category.objects.filter(name__in=category_names)
            article.categories.set(categories)

        if tag_names:
            article.tags.clear()
            tags = []
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                tags.append(tag)
            article.tags.set(tags)

        article.save()

        return JsonResponse({"message": "文章更新成功", "article_id": article.id}, status=200)

    return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
def delete_article(request, article_id):
    if not request.user.is_authenticated:
        return JsonResponse({"message": "用户未登录"}, status=401)
    if request.user.userprofile.role != 'admin':
        return JsonResponse({"message": "无权操作"}, status=403)
    if request.method == "DELETE":
        try:
            article = Article.objects.get(id=article_id)
            article.delete()
            return JsonResponse({"message": "文章已删除"}, status=200)
        except Article.DoesNotExist:
            return JsonResponse({"message": "文章不存在"}, status=404)
    else:
        return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
def like_article(request, article_id):
    if not request.user.is_authenticated:
        return JsonResponse({"message": "用户未登录"}, status=401)
    if request.method == "POST":
        try:
            article = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            return JsonResponse({"message": "文章不存在"}, status=404)

        # 未点赞时点赞，已点赞时取消点赞
        like, created = Like.objects.get_or_create(article=article, user=request.user)
        if not created:
            like.delete()
            return JsonResponse({"message": "取消点赞成功"}, status=200)
        return JsonResponse({"message": "点赞成功"}, status=200)

    return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
def submit_comment(request, article_id):
    if not request.user.is_authenticated:
        return JsonResponse({"message": "用户未登录"}, status=401)
    if request.method == "POST":
        try:
            article = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            return JsonResponse({"message": "文章不存在"}, status=404)

        content = request.POST.get("content")
        if not content:
            return JsonResponse({"message": "评论内容不能为空"}, status=400)
        # if not request.user.is_authenticated:
        #     #设置为id=1的用户，测试用
        #     request.user = User.objects.get(id=1)

        comment = Comment.objects.create(article=article, user=request.user, content=content)
        return JsonResponse({"message": "评论成功", "comment_id": comment.id}, status=201)

    return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
def retract_comment(request, comment_id):
    if request.method == "DELETE":
        user= request.user
        if not user.is_authenticated:
            return JsonResponse({"message": "用户未登录"}, status=401)
        try:
            comment = Comment.objects.get(id=comment_id)
            if user.userprofile.role !="admin" and comment.user != user:
                return JsonResponse({"message": "无权撤回评论"}, status=403)
            comment.delete()
            return JsonResponse({"message": "评论已撤回"}, status=200)
        except Comment.DoesNotExist:
            return JsonResponse({"message": "评论不存在或无权撤回"}, status=404)
    return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
def get_comments(request, article_id):
    if request.method == "GET":
        try:
            article = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            return JsonResponse({"message": "文章不存在"}, status=404)

        comments = article.comments.all().order_by("created_at")
        comment_list = [
            {
                "comment_id": comment.id,
                "user": comment.user.username,
                "user_name": comment.user.userprofile.name,
                "avatar": comment.user.userprofile.avatar.url,
                "content": comment.content,
                "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for comment in comments
        ]

        return JsonResponse({"comments": comment_list}, status=200)

    return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
def create_category(request):
    if not request.user.is_authenticated:
        return JsonResponse({"message": "用户未登录"}, status=401)
    if request.user.userprofile.role != 'admin':
        return JsonResponse({"message": "无权操作"}, status=403)
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        parent = request.POST.get("parent")
        if not name:
            return JsonResponse({"message": "分类名称不能为空"}, status=400)
        if Category.objects.filter(name=name).exists():
            return JsonResponse({"message": "分类已存在"}, status=400)
        if parent:
            try:
                parent_category = Category.objects.get(name=parent)
                parent_category_id = parent_category.id
            except Category.DoesNotExist:
                return JsonResponse({"message": "父分类不存在"}, status=404)
        else:
            parent_category_id = None

        category = Category.objects.create(name=name, description=description, parent_id=parent_category_id)

        return JsonResponse({"message": "分类创建成功", "category_id": category.id}, status=201)

    return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
def delete_category(request, category_id):
    if not request.user.is_authenticated:
        return JsonResponse({"message": "用户未登录"}, status=401)
    if request.user.userprofile.role != 'admin':
        return JsonResponse({"message": "无权操作"}, status=403)
    if request.method == "DELETE":
        try:
            category = Category.objects.get(id=category_id)
            category.delete()
            return JsonResponse({"message": "分类已删除"}, status=200)
        except Category.DoesNotExist:
            return JsonResponse({"message": "分类不存在"}, status=404)
    else:
        return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
def get_categories(request):
    if request.method == "GET":
        categories = Category.objects.all()
        category_list = [
            {
                "name": category.name,
                "description": category.description,
            }
            for category in categories
        ]

        return JsonResponse({"categories": category_list}, status=200)

    return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
def get_tags(request):
    if request.method == "GET":
        tags = Tag.objects.all()
        tag_list = [
            {
                "name": tag.name,
                "description": tag.description,
            }
            for tag in tags
        ]

        return JsonResponse({"tags": tag_list}, status=200)

    return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
def publish_article(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"message": "用户未登录"}, status=401)
        if request.user.is_authenticated and request.user.userprofile.role != 'admin':  # 检查是否为管理员
            return JsonResponse({"message": "无权限操作"}, status=403)

        # if not request.user.is_authenticated:
        #     # 设置为id=1的用户，测试用
        #     request.user = User.objects.get(id=1)

        title = request.POST.get("title")
        content = request.POST.get("content")
        tag_new = request.POST.get("tags")  # 标签名称
        status = request.POST.get("status", "published")  # 默认保存为草稿
        images = request.POST.get("images")  # 图片id列表

        # 验证输入字段
        if not title or not content:
            return JsonResponse({"message": "标题和内容为必填项"}, status=400)

        # 取首个图片id作为封面
        cover_image = None
        image_list = []
        if images:
            # 按逗号分割图片id
            image_list = list(map(int, images.split(",")))
            cover_image = MediaResource.objects.get(id=image_list[1]).file

        # 将content中的![img](1)图片标签按数组替换为图片url
        def replace_media(match):
            media_id = match.group(1)
            try:
                media = MediaResource.objects.get(id=image_list[int(media_id)])
                return f'![img]({media.file.url})'
            except MediaResource.DoesNotExist:
                return f'![img](内容丢失: {media_id})'
            except IndexError:
                return f'![img](数据库错误: {media_id})'

        pattern = r"!\[img\]\((.*?)\)"
        content_with_images = re.sub(pattern, replace_media, content)

        article = Article.objects.create(
            title=title,
            content=content_with_images,
            author=request.user,
            status=status,
            cover_image=cover_image
        )

        if tag_new:
            # 按空格分割标签，检测#开头的标签是否存在，不存在则创建
            tag_names = tag_new.split(" ")
            tags = []
            for tag_name in tag_names:
                if tag_name.startswith("#"):
                    tag_name = tag_name[1:]
                tag, created = Tag.objects.get_or_create(name=tag_name)
                tags.append(tag)
            article.tags.set(tags)

        return JsonResponse({"message": "文章创建成功", "article_id": article.id}, status=201)

    return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
def upload_medium(request):
    if not request.user.is_authenticated:
        return JsonResponse({"message": "用户未登录"}, status=401)
    if request.user.userprofile.role != 'admin':
        return JsonResponse({"message": "无权操作"}, status=403)
    if request.method == "POST":
        resource_file = request.FILES.get("file")
        reference_name = request.POST.get("fileName")
        resource_type = request.POST.get("resource_type")
        description = request.POST.get("description")
        resource_index = request.POST.get("index")

        # 校验
        if not resource_file or not reference_name:
            return JsonResponse({"message": "缺少必要参数"}, status=400)
        # 默认类型为image
        if not resource_type:
            resource_type = "image"
        # 保存资源
        resource = MediaResource.objects.create(
            file=resource_file,
            reference_name=reference_name,
            resource_type=resource_type,
            description=description
        )
        return JsonResponse({"message": "上传成功", "url": resource.file.url, "resource_index": resource_index, "resource_id": resource.id}, status=201)

    return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
def get_article(request, article_id):
    if request.method == "GET":
        try:
            if request.user.is_authenticated and request.user.userprofile.role != 'admin':
                article = Article.objects.get(id=article_id, status="published")
            else:
                article = Article.objects.get(id=article_id)

            article_detail = {
                "id": article.id,
                "title": article.title,
                "content": article.content,
                "time": article.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                "tags": [tag.name for tag in article.tags.all()],
                "likes": article.likes.count(),
                "cover_image": article.cover_image.url if article.cover_image else None,
            }
            return JsonResponse(article_detail, status=200)
        except Article.DoesNotExist:
            return JsonResponse({"message": "文章不存在"}, status=404)
    else:
        return JsonResponse({"message": "无效的请求方法"}, status=400)
