from django.urls import path
from .views import (
    hat_list_view,
    hat_create_view,
    hat_detail_view,
    hat_edit_view,
    hat_delete_view,
)

urlpatterns = [
    path("", hat_list_view, name="hat_list"),
    path("create/", hat_create_view, name="hat_create"),
    path("<int:pk>/", hat_detail_view, name="hat_detail"),
    path("<int:pk>/edit/", hat_edit_view, name="hat_edit"),
    path("<int:pk>/delete/", hat_delete_view, name="hat_delete"),
]
