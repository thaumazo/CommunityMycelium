from django.urls import path
from .views import (
    task_list_view,
    task_create_view,
    task_detail_view,
    task_edit_view,
    task_delete_view,
)

urlpatterns = [
    path("", task_list_view, name="task_list"),
    path("create/", task_create_view, name="task_create"),
    path("<int:pk>/", task_detail_view, name="task_detail"),
    path("<int:pk>/edit/", task_edit_view, name="task_edit"),
    path("<int:pk>/delete/", task_delete_view, name="task_delete"),
]
