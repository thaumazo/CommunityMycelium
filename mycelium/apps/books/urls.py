from django.urls import path
from .views import (
    book_list_view,
    book_create_view,
    book_detail_view,
    book_edit_view,
    book_delete_view,
)

urlpatterns = [
    path("", book_list_view, name="book_list"),
    path("create/", book_create_view, name="book_create"),
    path("<int:pk>/", book_detail_view, name="book_detail"),
    path("<int:pk>/edit/", book_edit_view, name="book_edit"),
    path("<int:pk>/delete/", book_delete_view, name="book_delete"),
]
