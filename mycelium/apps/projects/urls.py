from django.urls import path
from .views import (
    move_list_view,
    move_create_view,
    move_detail_view,
    move_edit_view,
    move_delete_view,
    move_story_import_view,
    move_story_visibility_update_view,
    move_story_visibility_bulk_update_view,
    move_community_note_decision_view,
    project_list_view,
    project_create_view,
    project_detail_view,
    project_edit_view,
    project_delete_view,
    project_story_import_view,
    project_story_visibility_update_view,
    project_story_visibility_bulk_update_view,
    project_community_note_decision_view,
)

urlpatterns = [
    path("", move_list_view, name="move_list"),
    path("create/", move_create_view, name="move_create"),
    path("<int:pk>/", move_detail_view, name="move_detail"),
    path("<int:pk>/import-stories/", move_story_import_view, name="move_story_import"),
    path("<int:pk>/stories/<int:story_pk>/visibility/", move_story_visibility_update_view, name="move_story_visibility_update"),
    path("<int:pk>/stories/visibility/bulk/", move_story_visibility_bulk_update_view, name="move_story_visibility_bulk_update"),
    path("<int:pk>/community-notes/<int:story_pk>/decision/", move_community_note_decision_view, name="move_community_note_decision"),
    path("<int:pk>/edit/", move_edit_view, name="move_edit"),
    path("<int:pk>/delete/", move_delete_view, name="move_delete"),

    # Legacy aliases kept temporarily for backward compatibility.
    path("", project_list_view, name="project_list"),
    path("create/", project_create_view, name="project_create"),
    path("<int:pk>/", project_detail_view, name="project_detail"),
    path("<int:pk>/import-stories/", project_story_import_view, name="project_story_import"),
    path("<int:pk>/stories/<int:story_pk>/visibility/", project_story_visibility_update_view, name="project_story_visibility_update"),
    path("<int:pk>/stories/visibility/bulk/", project_story_visibility_bulk_update_view, name="project_story_visibility_bulk_update"),
    path("<int:pk>/community-notes/<int:story_pk>/decision/", project_community_note_decision_view, name="project_community_note_decision"),
    path("<int:pk>/edit/", project_edit_view, name="project_edit"),
    path("<int:pk>/delete/", project_delete_view, name="project_delete"),
]
