from django.urls import path
from .views import login_view, register_view, home_view, user_list_view, logout_view

urlpatterns = [
    path("", home_view, name="home"),
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("users/", user_list_view, name="user_list"),
    path("logout/", logout_view, name="logout"),
]
