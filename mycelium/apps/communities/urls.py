from django.urls import path
from .views import (
    community_list_view,
    community_create_view,
    community_detail_view,
    community_edit_view,
    community_delete_view,
)

urlpatterns = [
    path("", community_list_view, name="community_list"),
    path("create/", community_create_view, name="community_create"),
    path("<int:pk>/", community_detail_view, name="community_detail"),
    path("<int:pk>/edit/", community_edit_view, name="community_edit"),
    path("<int:pk>/delete/", community_delete_view, name="community_delete"),
]
