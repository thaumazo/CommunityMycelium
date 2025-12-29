from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    api_login,
    api_register,
    api_logout,
    api_user_me,
    UserViewSet,
    BioregionViewSet,
    ChallengeViewSet,
    CommunityViewSet,
    ProjectViewSet,
    TaskViewSet,
    StoryViewSet,
)

# Create a router for viewsets
router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"bioregions", BioregionViewSet, basename="bioregion")
router.register(r"challenges", ChallengeViewSet, basename="challenge")
router.register(r"communities", CommunityViewSet, basename="community")
router.register(r"projects", ProjectViewSet, basename="project")
router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"stories", StoryViewSet, basename="story")

urlpatterns = [
    # Authentication endpoints
    path("auth/login/", api_login, name="api_login"),
    path("auth/register/", api_register, name="api_register"),
    path("auth/logout/", api_logout, name="api_logout"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="api_token_refresh"),
    path("auth/me/", api_user_me, name="api_user_me"),
    # ViewSet routes
    path("", include(router.urls)),
]