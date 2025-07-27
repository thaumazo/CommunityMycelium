from django.urls import path
from .views import (
    socialrole_list_view,
    socialrole_create_view,
    socialrole_detail_view,
    socialrole_edit_view,
    socialrole_delete_view,
)

urlpatterns = [
    path("", socialrole_list_view, name="socialrole_list"),
    path("create/", socialrole_create_view, name="socialrole_create"),
    path("<int:pk>/", socialrole_detail_view, name="socialrole_detail"),
    path("<int:pk>/edit/", socialrole_edit_view, name="socialrole_edit"),
    path("<int:pk>/delete/", socialrole_delete_view, name="socialrole_delete"),
]
