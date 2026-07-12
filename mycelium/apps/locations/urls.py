from django.urls import path
from .views import (
    location_list_view,
    location_create_view,
    location_detail_view,
    location_edit_view,
    location_delete_view,
    location_geocode_lookup_view,
)

urlpatterns = [
    path("", location_list_view, name="location_list"),
    path("create/", location_create_view, name="location_create"),
    path("geocode/", location_geocode_lookup_view, name="location_geocode_lookup"),
    path("<int:pk>/", location_detail_view, name="location_detail"),
    path("<int:pk>/edit/", location_edit_view, name="location_edit"),
    path("<int:pk>/delete/", location_delete_view, name="location_delete"),
]
