from django.urls import path
from .views import (
    student_list_view,
    student_create_view,
    student_detail_view,
    student_edit_view,
    student_delete_view,
)

urlpatterns = [
    path("", student_list_view, name="student_list"),
    path("create/", student_create_view, name="student_create"),
    path("<int:pk>/", student_detail_view, name="student_detail"),
    path("<int:pk>/edit/", student_edit_view, name="student_edit"),
    path("<int:pk>/delete/", student_delete_view, name="student_delete"),
]
