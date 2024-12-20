from django.urls import path
from . import views

urlpatterns = [
    path("create-post/", views.create_post),
    path("get-post/", views.get_post),
    path("get-all-posts/", views.get_all_posts),
    path("create-comment/", views.create_comment),
    path("get-comment/", views.get_comment),
    path("get-comments/", views.get_comments),
    path("edit-post/", views.edit_post),
    path("delete-post/", views.delete_post),
    path("delete-comment/", views.delete_comment),
    path("like-post-switch/", views.like_post_switch),
    path("report-post/", views.report_post),
    path("report-comment/", views.report_comment),
    path("get-reports/", views.get_reports),
    path("resolve-report/", views.resolve_report),
    path("get-feedbacks/", views.get_feedbacks),
    path("submit-feedback/", views.submit_feedback),
    path("resolve-feedback/", views.resolve_feedback),
]
