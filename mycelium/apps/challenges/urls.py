from django.urls import path
from .views import (
    challenge_list_view,
    challenge_create_view,
    challenge_detail_view,
    challenge_edit_view,
    challenge_delete_view,
)

urlpatterns = [
    path("", challenge_list_view, name="challenge_list"),
    path("create/", challenge_create_view, name="challenge_create"),
    path("<int:pk>/", challenge_detail_view, name="challenge_detail"),
    path("<int:pk>/edit/", challenge_edit_view, name="challenge_edit"),
    path("<int:pk>/delete/", challenge_delete_view, name="challenge_delete"),
]
