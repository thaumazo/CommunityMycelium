from django.urls import path
from .views import meeting_list_view

urlpatterns = [
    path("", meeting_list_view, name="meeting_list"),
]
