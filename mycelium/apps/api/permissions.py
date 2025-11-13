from rest_framework import permissions
from apps.acl.utils import is_permitted


class ACLPermission(permissions.BasePermission):
    """
    Custom permission class that integrates with the existing ACL system.
    """

    def has_permission(self, request, view):
        """
        Check if user has model-level permission.
        """
        if not request.user or not request.user.is_authenticated:
            return False

        # Map HTTP methods to ACL actions
        action_map = {
            "GET": "view",
            "POST": "add",
            "PUT": "change",
            "PATCH": "change",
            "DELETE": "delete",
        }

        action = action_map.get(request.method)
        if not action:
            return False

        # For list views, check model-level permission
        if hasattr(view, "queryset") and view.queryset is not None:
            model = view.queryset.model
            model_name = f"{model._meta.app_label}.{model._meta.model_name}"
            return is_permitted(request.user, action, model_name)

        return True

    def has_object_permission(self, request, view, obj):
        """
        Check if user has object-level permission.
        """
        if not request.user or not request.user.is_authenticated:
            return False

        # Map HTTP methods to ACL actions
        action_map = {
            "GET": "view",
            "PUT": "change",
            "PATCH": "change",
            "DELETE": "delete",
        }

        action = action_map.get(request.method)
        if not action:
            return False

        return is_permitted(request.user, action, obj)
