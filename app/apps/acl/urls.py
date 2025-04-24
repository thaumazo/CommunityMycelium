from django.urls import path
from .views import (
    content_type_list_view,
    object_list_view,
    object_user_permission_detail_view,
    object_user_permission_form_view,
)

urlpatterns = [
    path("", content_type_list_view, name="content_type_list"),
    path("<int:content_type_id>/", object_list_view, name="object_list"),
    path(
        "<int:content_type_id>/<int:object_id>/",
        object_user_permission_detail_view,
        name="object_user_permission_detail",
    ),
    path(
        "<int:content_type_id>/<int:object_id>/<int:user_id>/",
        object_user_permission_form_view,
        name="object_user_permission_form",
    ),
]
