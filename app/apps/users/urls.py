from django.urls import path
from .views import (
    user_list_view,
    user_create_view,
    logout_view,
    login_view,
    register_view,
)

urlpatterns = [
    path("", user_list_view, name="user_list"),
    path("create/", user_create_view, name="user_create"),
    path("logout/", logout_view, name="logout"),
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
]
