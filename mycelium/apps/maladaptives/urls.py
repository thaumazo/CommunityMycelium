from django.urls import path
from .views import (
    maladaptive_list_view,
    maladaptive_create_view,
    maladaptive_detail_view,
    maladaptive_edit_view,
    maladaptive_delete_view,
)

urlpatterns = [
    path("", maladaptive_list_view, name="maladaptive_list"),
    path("create/", maladaptive_create_view, name="maladaptive_create"),
    path("<int:pk>/", maladaptive_detail_view, name="maladaptive_detail"),
    path("<int:pk>/edit/", maladaptive_edit_view, name="maladaptive_edit"),
    path("<int:pk>/delete/", maladaptive_delete_view, name="maladaptive_delete"),
]
