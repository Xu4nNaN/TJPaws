from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.user_login),
    path("add-admin/", views.add_admin),
    path("change-user-status/", views.change_user_status),
    path("get-userprofile/", views.get_userprofile),
    # path("register/", views.register),
    path("avatar/upload/", views.upload_avatar),
    path("profile/update/", views.update_profile),
    path("get-my-profile/", views.get_my_profile),
    path("upgrade-to-admin-with-key/", views.upgrade_to_admin_with_key),
]