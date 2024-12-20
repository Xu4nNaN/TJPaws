from django.shortcuts import render
from .models import Post, Comment, Like_Post, Like_Comment, Report
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from notification.utils import create_notification
import json


# Create your views here.

@csrf_exempt
# @login_required
def create_post(request):
    if request.method == "POST":
        author = request.user
        if not author.is_authenticated:
            return JsonResponse({"message": "用户未登录"}, status=401)
        title = request.POST.get("title")
        content = request.POST.get("content")
        if title is None or content is None:
            return JsonResponse({"message": "缺少参数"}, status=400)
        if author.userprofile.is_banned:
            return JsonResponse({"message": "用户被封禁"}, status=403)
        post = Post.objects.create(author=author, title=title, content=content)
        if post is None:
            return JsonResponse({"message": "发布失败"}, status=500)
        return JsonResponse({"message": "发布成功", "post_id": post.id}, status=200)
    else:
        return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
def get_post(request):
    if request.method == "GET":
        post_id = request.GET.get("post_id")
        if post_id is None:
            return JsonResponse({"message": "缺少参数"}, status=400)
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return JsonResponse({"message": "帖子不存在"}, status=404)
        return JsonResponse({"message": "获取成功", "title": post.title, "content": post.content,
                             "author": post.author.userprofile.name, "created_time": post.created_time,
                             "author_id": post.author.username
                             }, status=200)
    else:
        return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
def get_all_posts(request):
    if request.method == "GET":
        posts = Post.objects.all().order_by('-created_time')
        post_list = [{"post_id": post.id, "title": post.title, "content": post.content,
                      "author": post.author.userprofile.name, "created_time": post.created_time,
                      "author_id": post.author.username} for post in posts]
        return JsonResponse({"message": "获取成功", "post_list": post_list}, status=200)
    else:
        return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
# @login_required
def create_comment(request):
    if request.method == "POST":
        author = request.user
        if not author.is_authenticated:
            return JsonResponse({"message": "用户未登录"}, status=401)
        post_id = request.POST.get("post_id")
        parent_id = request.POST.get("parent_id")
        content = request.POST.get("content")
        if post_id is None or content is None:
            return JsonResponse({"message": "缺少参数"}, status=400)
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return JsonResponse({"message": "帖子不存在"}, status=404)
        try:
            parent = Comment.objects.get(id=parent_id) if parent_id is not None else None
        except Comment.DoesNotExist:
            return JsonResponse({"message": "父评论不存在"}, status=404)
        if author.userprofile.is_banned:
            return JsonResponse({"message": "用户被封禁"}, status=403)
        comment = Comment.objects.create(author=author, content=content, post=post, parent=parent)
        if comment is None:
            return JsonResponse({"message": "评论失败"}, status=500)
        # 生成通知
        create_notification(post.author, "comment",
                            f"{author.userprofile.name} 评论了你的" + ("评论" if parent is not None else "帖子"),
                            post.id)
        return JsonResponse({"message": "发布成功", "comment_id": comment.id}, status=200)
    else:
        return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
def get_comment(request):
    if request.method == "GET":
        comment_id = request.GET.get("comment_id")
        if comment_id is None:
            return JsonResponse({"message": "缺少参数"}, status=400)
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return JsonResponse({"message": "评论不存在"}, status=404)
        return JsonResponse({"message": "获取成功", "content": comment.content,
                             "author": comment.author.userprofile.name, "created_time": comment.created_time
                             }, status=200)
    else:
        return JsonResponse({"message": "无效的请求方法"}, status=400)

@csrf_exempt
def get_comments(request):
    if request.method == "GET":
        post_id = request.GET.get("post_id")
        if post_id is None:
            return JsonResponse({"message": "缺少参数"}, status=400)
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return JsonResponse({"message": "帖子不存在"}, status=404)
        comments = Comment.objects.filter(post=post).order_by('created_time')
        comment_list = [{"comment_id": comment.id, "content": comment.content,
                         "author": comment.author.userprofile.name, "created_time": comment.created_time
                         } for comment in comments]
        return JsonResponse({"message": "获取成功", "comment_list": comment_list}, status=200)
    else:
        return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
# @login_required
def edit_post(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"message": "用户未登录"}, status=401)
        # 获取请求体中的数据
        post_id = request.POST.get("post_id")
        title = request.POST.get("title")
        content = request.POST.get("content")

        if post_id is None or title is None or content is None:
            return JsonResponse({"message": "缺少参数"}, status=400)

        # 获取帖子对象
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return JsonResponse({"message": "帖子不存在"}, status=404)

        # 检查用户权限
        if request.user != post.author:
            return JsonResponse({"message": "无权操作"}, status=403)

        # 更新帖子并保存
        post.title = title
        post.content = content
        post.save()

        return JsonResponse({"message": "修改成功"}, status=200)

    else:
        return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
# @login_required
def delete_post(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"message": "用户未登录"}, status=401)
        post_id = request.POST.get("post_id")
        if post_id is None:
            return JsonResponse({"message": "缺少参数"}, status=400)
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return JsonResponse({"message": "帖子不存在"}, status=404)
        if request.user != post.author and request.user.userprofile.role != "admin":
            return JsonResponse({"message": "无权操作"}, status=403)
        post.delete()
        if request.user.userprofile.role == "admin":
            create_notification(post.author, "system", f"您的帖子 {post.title} 已被管理员删除",0)
        return JsonResponse({"message": "删除成功"}, status=200)
    else:
        return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
def delete_comment(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"message": "用户未登录"}, status=401)
        comment_id = request.POST.get("comment_id")
        if comment_id is None:
            return JsonResponse({"message": "缺少参数"}, status=400)
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return JsonResponse({"message": "评论不存在"}, status=404)
        if request.user != comment.author and request.user.userprofile.role != "admin":
            return JsonResponse({"message": "无权操作"}, status=403)
        comment.delete()
        if request.user.userprofile.role == "admin":
            create_notification(comment.author, "system", f"您的评论 {comment.content} 已被管理员删除",0)
        return JsonResponse({"message": "删除成功"}, status=200)
    else:
        return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
# @login_required
def like_post_switch(request):
    if request.method == "POST":
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({"message": "用户未登录"}, status=401)
        post_id = request.POST.get("post_id")
        if post_id is None:
            return JsonResponse({"message": "缺少参数"}, status=400)
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return JsonResponse({"message": "帖子不存在"}, status=404)
        like, created = Like_Post.objects.get_or_create(user=user, content=post)
        if not created:
            like.delete()
            return JsonResponse({"message": "取消点赞成功"}, status=200)
        if like is None:
            return JsonResponse({"message": "点赞失败"}, status=500)
        # 生成通知
        create_notification(post.author, "like", f"{user.userprofile.name} 点赞了你的帖子", post.id)
        return JsonResponse({"message": "点赞成功"}, status=200)

    else:
        return JsonResponse({"message": "无效的请求方法"}, status=400)


# @csrf_exempt
# @login_required
# def unlike_post(request):
#     if request.method == "POST":
#         user = request.user
#         post_id = request.POST.get("post_id")
#         if post_id is None:
#             return JsonResponse({"message": "缺少参数"}, status=400)
#         post = Post.objects.get(id=post_id)
#         if post is None:
#             return JsonResponse({"message": "帖子不存在"}, status=404)
#         try:
#             like = Like_Post.objects.get(user=user, content=post)
#         except Like_Post.DoesNotExist:
#             return JsonResponse({"message": "未点赞"}, status=400)
#         like.delete()
#         return JsonResponse({"message": "取消点赞成功"}, status=200)
#
#     else:
#         return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
# @login_required
def report_post(request):
    if request.method == "POST":
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({"message": "用户未登录"}, status=401)
        post_id = request.POST.get("post_id")
        reason = request.POST.get("reason")
        if post_id is None or reason is None:
            return JsonResponse({"message": "缺少参数"}, status=400)
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return JsonResponse({"message": "帖子不存在"}, status=404)
        report = Report.objects.create(target_type="post", target_id=post_id, reporter=user, reason=reason)
        if report is None:
            return JsonResponse({"message": "举报失败"}, status=500)
        return JsonResponse({"message": "举报成功"}, status=200)

    else:
        return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
# @login_required
def report_comment(request):
    if request.method == "POST":
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({"message": "用户未登录"}, status=401)
        comment_id = request.POST.get("comment_id")
        reason = request.POST.get("reason")
        if comment_id is None or reason is None:
            return JsonResponse({"message": "缺少参数"}, status=400)
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return JsonResponse({"message": "评论不存在"}, status=404)
        report = Report.objects.create(target_type="comment", target_id=comment_id, reporter=user, reason=reason)
        if report is None:
            return JsonResponse({"message": "举报失败"}, status=500)
        return JsonResponse({"message": "举报成功"}, status=200)

    else:
        return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
# @login_required
def get_reports(request):
    if request.method == "GET":
        if not request.user.is_authenticated:
            return JsonResponse({"message": "用户未登录"}, status=401)
        reports=Report.objects.all()
        report_list = []
        for report in reports:
            if report.target_type == "post":
                try:
                    target = Post.objects.get(id=report.target_id)
                    report_list.append(
                        {"report_id": report.id, "target_type": report.target_type, "target_id": report.target_id,
                         "reporter": report.reporter.userprofile.name, "reason": report.reason, "post_id": target.id,
                         "status":report.status, "admin_notes":report.admin_notes})
                except Post.DoesNotExist:
                    report_list.append(
                        {"report_id": report.id, "target_type": report.target_type, "target_id": report.target_id,
                         "reporter": report.reporter.userprofile.name, "reason": report.reason, "post_id": "deleted",
                         "status":report.status, "admin_notes":report.admin_notes})
            elif report.target_type == "comment":
                try:
                    target = Comment.objects.get(id=report.target_id)
                    report_list.append(
                        {"report_id": report.id, "target_type": report.target_type, "target_id": report.target_id,
                         "reporter": report.reporter.userprofile.name, "reason": report.reason, "post_id": target.post.id,
                         "status":report.status, "admin_notes":report.admin_notes})
                except Comment.DoesNotExist:
                    report_list.append(
                        {"report_id": report.id, "target_type": report.target_type, "target_id": report.target_id,
                         "reporter": report.reporter.userprofile.name, "reason": report.reason, "post_id": "deleted",
                         "status":report.status, "admin_notes":report.admin_notes})
        # report_list = [{"report_id": report.id, "target_type": report.target_type, "target_id": report.target_id,
        #                 "reporter": report.reporter.userprofile.name, "reason": report.reason} for report in reports]
        return JsonResponse({"message": "获取成功", "report_list": report_list}, status=200)
    else:
        return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
def resolve_report(request):
    if request.method == "POST":
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({"message": "用户未登录"}, status=401)
        if user.userprofile.role != "admin":
            return JsonResponse({"message": "无权操作"}, status=403)
        report_id = request.POST.get("report_id")
        admin_notes = request.POST.get("admin_notes")
        if report_id is None:
            return JsonResponse({"message": "缺少参数"}, status=400)
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return JsonResponse({"message": "举报不存在"}, status=404)
        report.status = "resolved"
        report.admin_notes = admin_notes
        report.save()
        create_notification(report.reporter, "system", f"您的举报已被处理，处理结果：{admin_notes}",0)
        return JsonResponse({"message": "处理成功"}, status=200)
    else:
        return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
def get_feedbacks(request):
    if request.method == "GET":
        if not request.user.is_authenticated:
            return JsonResponse({"message": "用户未登录"}, status=401)
        if request.user.userprofile.role != "admin":
            return JsonResponse({"message": "无权操作"}, status=403)
        feedbacks = Report.objects.filter(target_id=0)
        feedback_list = [{"feedback_id": feedback.id,"feedback_notes": feedback.reason,
                          "status": feedback.status, "admin_notes": feedback.admin_notes}
                         for feedback in feedbacks]
        return JsonResponse({"message": "获取成功", "feedback_list": feedback_list}, status=200)
    else:
        return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
def submit_feedback(request):
    if request.method == "POST":
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({"message": "用户未登录"}, status=401)
        feedback_notes = request.POST.get("feedback_notes")
        if feedback_notes is None:
            return JsonResponse({"message": "缺少参数"}, status=400)
        feedback = Report.objects.create(target_type="post", target_id=0, reporter=user, reason=feedback_notes)
        if feedback is None:
            return JsonResponse({"message": "反馈失败"}, status=500)
        return JsonResponse({"message": "反馈成功"}, status=200)
    else:
        return JsonResponse({"message": "无效的请求方法"}, status=400)


@csrf_exempt
def resolve_feedback(request):
    if request.method == "POST":
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({"message": "用户未登录"}, status=401)
        if user.userprofile.role != "admin":
            return JsonResponse({"message": "无权操作"}, status=403)
        feedback_id = request.POST.get("feedback_id")
        admin_notes = request.POST.get("admin_notes")
        if feedback_id is None:
            return JsonResponse({"message": "缺少参数"}, status=400)
        try:
            feedback = Report.objects.get(id=feedback_id)
        except Report.DoesNotExist:
            return JsonResponse({"message": "反馈不存在"}, status=404)
        feedback.status = "resolved"
        feedback.admin_notes = admin_notes
        feedback.save()
        create_notification(feedback.reporter, "system", f"您的反馈已被处理，处理结果：{admin_notes}",0)
        return JsonResponse({"message": "处理成功"}, status=200)
    else:
        return JsonResponse({"message": "无效的请求方法"}, status=400)

