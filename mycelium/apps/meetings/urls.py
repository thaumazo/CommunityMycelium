from django.urls import path
from .views import (
    meeting_list_view,
    meeting_create_view,
    meeting_detail_view,
    meeting_edit_view,
    meeting_delete_view,
)

urlpatterns = [
    path("", meeting_list_view, name="meeting_list"),
    path("create/", meeting_create_view, name="meeting_create"),
    path("<int:pk>/", meeting_detail_view, name="meeting_detail"),
    path("<int:pk>/edit/", meeting_edit_view, name="meeting_edit"),
    path("<int:pk>/delete/", meeting_delete_view, name="meeting_delete"),
]
