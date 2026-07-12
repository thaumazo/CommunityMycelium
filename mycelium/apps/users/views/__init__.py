"""
Import all views from the users app to maintain backward compatibility.
"""

# Import all views from the main views module
from .main import (
    login_view,
    register_view,
    user_list_view,
    user_create_view,
    logout_view,
    user_detail_view,
    user_edit_view,
    user_permission_edit_view,
    user_delete_view,
    user_character_view,
    pending_users_view,
    approve_user_view,
    reject_user_view,
    create_invite_view,
)

# Make them available when importing from apps.users.views
__all__ = [
    'login_view',
    'register_view',
    'user_list_view',
    'user_create_view',
    'logout_view',
    'user_detail_view',
    'user_edit_view',
    'user_permission_edit_view',
    'user_delete_view',
    'user_character_view',
    'pending_users_view',
    'approve_user_view',
    'reject_user_view',
    'create_invite_view',
]
