from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MeetingViewSet

router = DefaultRouter()
router.register(r"", MeetingViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
