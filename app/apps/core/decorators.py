from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test


def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""

    def in_groups(u):
        if u.is_authenticated:
            if u.is_superuser or u.groups.filter(name__in=group_names).exists():
                return True
        return False

    return user_passes_test(in_groups)


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
