from django.urls import path

from . import views

urlpatterns = [
    path("animal/integer/", views.search_animals_by_integer),
    path("animal/string/", views.search_animals_by_string),
    path("animal/distance/", views.search_animals_by_distance),
]