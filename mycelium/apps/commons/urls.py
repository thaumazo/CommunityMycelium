from django.urls import path
from .views import (
    commons_list_view,
    commons_create_view,
    commons_detail_view,
    commons_edit_view,
    commons_delete_view,
    commons_apply_view,
    commons_application_respond_view,
    commons_invite_create_view,
    commons_invite_respond_view,
)

urlpatterns = [
    path("", commons_list_view, name="commons_list"),
    path("create/", commons_create_view, name="commons_create"),
    path("<int:pk>/", commons_detail_view, name="commons_detail"),
    path("<int:pk>/edit/", commons_edit_view, name="commons_edit"),
    path("<int:pk>/delete/", commons_delete_view, name="commons_delete"),
    path("<int:pk>/apply/", commons_apply_view, name="commons_apply"),
    path("<int:pk>/applications/<int:application_pk>/respond/", commons_application_respond_view, name="commons_application_respond"),
    path("<int:pk>/invite/", commons_invite_create_view, name="commons_invite_create"),
    path("<int:pk>/invites/<int:invite_pk>/respond/", commons_invite_respond_view, name="commons_invite_respond"),
]
