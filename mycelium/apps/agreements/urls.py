from django.urls import path
from .views import (
    agreement_list_view,
    agreement_create_view,
    agreement_detail_view,
    agreement_edit_view,
    agreement_delete_view,
)

urlpatterns = [
    path("", agreement_list_view, name="agreement_list"),
    path("create/", agreement_create_view, name="agreement_create"),
    path("<int:pk>/", agreement_detail_view, name="agreement_detail"),
    path("<int:pk>/edit/", agreement_edit_view, name="agreement_edit"),
    path("<int:pk>/delete/", agreement_delete_view, name="agreement_delete"),
]
