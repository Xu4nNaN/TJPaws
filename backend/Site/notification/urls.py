from django.urls import path

from . import views

urlpatterns = [
    path('send-notification/', views.send_notification, name='send_notification'),
    path('get-notifications/', views.get_notifications, name='get_notifications'),
]