from django.urls import path

from . import views

urlpatterns = [
    path('animal/create/', views.create_animal, name='create_animal'),
    path('animal/update/<int:animal_id>/', views.update_animal, name='update_animal'),
    path('animal/delete/<int:animal_id>/', views.delete_animal, name='delete_animal'),
    path('animal/get/<int:animal_id>/', views.get_animal, name='get_animal'),
    path('animal/gets/', views.get_animals, name='get_animals'),
    path('animal/<int:animal_id>/feedback/', views.submit_feedback, name='submit_feedback'),
    path('animal/feedbacks/', views.get_feedbacks, name='get_feedbacks'),
    path('animal/feedback/<int:feedback_id>/', views.update_feedback, name='update_feedback'),
    path('animal/leaderboard/get/', views.get_animal_leaderboard, name='get_animal_leaderboard'),
    path('animal/leaderboard/set/', views.set_animal_score, name='set_animal_score'),
    path('animal/like-animal-switch/', views.like_animal_switch, name='like_animal_switch'),
    path('animal/publish/', views.publish_animal, name='create_animal'),
    path('medium/upload/', views.upload_medium, name='upload_medium'),
]
