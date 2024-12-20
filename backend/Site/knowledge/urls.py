from django.urls import path

from . import views

urlpatterns = [
    path('article/create/', views.create_article, name='create_article'),
    path('article/update/<int:article_id>/', views.update_article, name='update_article'),
    path('article/delete/<int:article_id>/', views.delete_article, name='delete_article'),
    path('article/get/<int:article_id>/', views.get_article, name='get_article'),
    path('article/gets/', views.get_articles, name='get_articles'),
    path('article/<int:article_id>/like/', views.like_article, name='like_article'),
    path('comment/<int:article_id>/', views.submit_comment, name='submit_comment'),
    path('comment/retract/<int:comment_id>/', views.retract_comment, name='retract_comment'),
    path('comments/<int:article_id>/', views.get_comments, name='get_comments'),
    path('category/create/', views.create_category, name='create_category'),
    path('category/delete/<int:category_id>/', views.delete_category, name='delete_category'),
    path('category/gets/', views.get_categories, name='get_categories'),
    path('tag/gets/', views.get_tags, name='get_tags'),
    path('media/upload/', views.upload_media, name='create_media_resource'),
    path('media/delete/<str:reference_name>/', views.delete_media, name='delete_media_resource'),
    path('media/get/<str:reference_name>/', views.get_media, name='get_media_resource'),
    path('media/gets/', views.get_all_media, name='get_media_resources'),
    path('media/thumbnails/', views.get_thumbnails, name='get_thumbnails'),
    path('media/download/<str:reference_name>/', views.download_media, name='get_media_resource'),
    path('article/publish/', views.publish_article, name='publish'),
    path('medium/upload/', views.upload_medium, name='upload_medium'),
]