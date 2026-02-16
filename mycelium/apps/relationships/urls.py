from django.urls import path
from .views import (
    relationship_list_view,
    relationship_create_view,
    relationship_detail_view,
    relationship_edit_view,
    relationship_delete_view,
    relationship_proposal_create_view,
    relationship_proposal_detail_view,
)

urlpatterns = [
    path("", relationship_list_view, name="relationship_list"),
    path("proposals/create/", relationship_proposal_create_view, name="relationship_proposal_create"),
    path("proposals/<int:pk>/", relationship_proposal_detail_view, name="relationship_proposal_detail"),
    path("create/", relationship_create_view, name="relationship_create"),
    path("<int:pk>/", relationship_detail_view, name="relationship_detail"),
    path("<int:pk>/edit/", relationship_edit_view, name="relationship_edit"),
    path("<int:pk>/delete/", relationship_delete_view, name="relationship_delete"),
]
