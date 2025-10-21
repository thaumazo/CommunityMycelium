from django.urls import path
from .views import (
    resolution_list_view,
    resolution_create_view,
    resolution_detail_view,
    resolution_edit_view,
    resolution_delete_view,
)

urlpatterns = [
    path("", resolution_list_view, name="resolution_list"),
    path("create/", resolution_create_view, name="resolution_create"),
    path("<int:pk>/", resolution_detail_view, name="resolution_detail"),
    path("<int:pk>/edit/", resolution_edit_view, name="resolution_edit"),
    path("<int:pk>/delete/", resolution_delete_view, name="resolution_delete"),
]
