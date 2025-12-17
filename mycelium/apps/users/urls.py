from django.urls import path
from .views import (
    # List
    user_list_view,
    # CRUD
    user_create_view,
    user_detail_view,
    user_edit_view,
    user_permission_edit_view,
    user_delete_view,
    # Auth
    logout_view,
    login_view,
    register_view,
    # Character
    user_character_view,
    # Approval
    pending_users_view,
    approve_user_view,
    reject_user_view,
)
from .views.google_auth import (
    google_auth_start,
    google_auth_callback,
    google_auth_disconnect,
    google_drive_browser,
)

urlpatterns = [
    path("", user_list_view, name="user_list"),
    path("create/", user_create_view, name="user_create"),
    path("<int:pk>/", user_detail_view, name="user_detail"),
    path("<int:pk>/edit/", user_edit_view, name="user_edit"),
    path(
        "<int:pk>/permission_edit/",
        user_permission_edit_view,
        name="user_permission_edit",
    ),
    path("<int:pk>/delete/", user_delete_view, name="user_delete"),
    path("logout/", logout_view, name="logout"),
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("<int:pk>/character/", user_character_view, name="user_character"),
    path("pending/", pending_users_view, name="pending_users"),
    path("<int:pk>/approve/", approve_user_view, name="approve_user"),
    path("<int:pk>/reject/", reject_user_view, name="reject_user"),
    # Google OAuth
    path("google/auth/start/", google_auth_start, name="google_auth_start"),
    path("google/auth/callback/", google_auth_callback, name="google_auth_callback"),
    path("google/auth/disconnect/", google_auth_disconnect, name="google_auth_disconnect"),
    path("google/drive/browse/", google_drive_browser, name="google_drive_browser"),
]
