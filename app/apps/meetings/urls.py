from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MeetingViewSet, meeting_list_view

router = DefaultRouter()
router.register(r"", MeetingViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("list/", meeting_list_view, name="meeting_list"),
]
