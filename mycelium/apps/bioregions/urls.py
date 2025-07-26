from django.urls import path
from .views import (
    bioregion_list_view,
    bioregion_create_view,
    bioregion_detail_view,
    bioregion_edit_view,
    bioregion_delete_view,
)

urlpatterns = [
    path("", bioregion_list_view, name="bioregion_list"),
    path("create/", bioregion_create_view, name="bioregion_create"),
    path("<int:pk>/", bioregion_detail_view, name="bioregion_detail"),
    path("<int:pk>/edit/", bioregion_edit_view, name="bioregion_edit"),
    path("<int:pk>/delete/", bioregion_delete_view, name="bioregion_delete"),
]
