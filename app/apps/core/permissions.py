from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test


class PermissionService:
    """Centralized service for handling permissions"""

    @staticmethod
    def has_role(user, role):
        """Check if user has a specific role"""
        if user.is_superuser:
            return True
        return user.groups.filter(name=role).exists()

    @staticmethod
    def has_any_role(user, roles):
        """Check if user has any of the specified roles"""
        if user.is_superuser:
            return True
        return user.groups.filter(name__in=roles).exists()

    @staticmethod
    def can_manage_users(user):
        """Check if user can manage users"""
        if user.is_superuser:
            return True
        return user.has_perm("users.can_manage_users")

    @staticmethod
    def can_manage_meetings(user):
        """Check if user can manage meetings"""
        if user.is_superuser:
            return True
        return user.has_perm("users.can_manage_meetings")

    @staticmethod
    def can_view_meeting(user, meeting):
        """Check if user can view a specific meeting"""
        if user.is_superuser:
            return True
        return user.groups.filter(name__in=["viewer", "editor", "admin"]).exists()

    @staticmethod
    def can_edit_meeting(user, meeting):
        """Check if user can edit a specific meeting"""
        if user.is_superuser:
            return True
        if meeting.created_by == user:
            return True
        return user.groups.filter(name__in=["editor", "admin"]).exists()

    @staticmethod
    def can_delete_meeting(user, meeting):
        """Check if user can delete a specific meeting"""
        if user.is_superuser:
            return True
        if meeting.created_by == user:
            return True
        return user.groups.filter(name="admin").exists()


# Decorators for view functions
def role_required(*roles):
    """Requires user membership in at least one of the roles passed in."""

    def in_roles(u):
        return PermissionService.has_any_role(u, roles)

    return user_passes_test(in_roles)


def permission_required(permission):
    """Requires user to have the specified permission."""

    def check_perms(user):
        if user.is_superuser:
            return True
        return user.has_perm(permission)

    return user_passes_test(check_perms)


def object_permission_required(model_class, permission_check):
    """
    Decorator for checking object-level permissions.
    permission_check should be a string name of the method to call on the model
    (e.g., 'can_edit', 'can_delete')
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            obj = model_class.objects.get(pk=kwargs["pk"])
            check_method = getattr(obj, permission_check)
            if not check_method(request.user):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
