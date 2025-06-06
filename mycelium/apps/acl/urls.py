from django.urls import path
from .views import (
    acl_content_type_list_view,
    acl_object_list_view,
    acl_object_permission_form_step_1_view,
    acl_object_permission_form_step_2_view,
)

urlpatterns = [
    path("", acl_content_type_list_view, name="acl_content_type_list"),
    path("<int:content_type_id>/", acl_object_list_view, name="acl_object_list"),
    path(
        "<int:content_type_id>/<int:object_id>/",
        acl_object_permission_form_step_1_view,
        name="acl_object_permission_form_step_1",
    ),
    path(
        "<int:content_type_id>/<int:object_id>/<int:user_id>/",
        acl_object_permission_form_step_2_view,
        name="acl_object_permission_form_step_2",
    ),
]
