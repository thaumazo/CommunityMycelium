from django.urls import path
from .views import (
    capital_list_view,
    capital_create_view,
    capital_detail_view,
    capital_edit_view,
    capital_delete_view,
)

urlpatterns = [
    path("", capital_list_view, name="capital_list"),
    path("create/", capital_create_view, name="capital_create"),
    path("<int:pk>/", capital_detail_view, name="capital_detail"),
    path("<int:pk>/edit/", capital_edit_view, name="capital_edit"),
    path("<int:pk>/delete/", capital_delete_view, name="capital_delete"),
]
