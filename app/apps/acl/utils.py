from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied
from django.http import Http404
from .models import ObjectPermission


def can(user, action, obj):
    """Check if a user has permission to perform `action` on `obj`."""
    # First check if user has model-level permission through groups
    model_permission = f"{action}_{obj._meta.model_name}"
    if user.has_perm(f"{obj._meta.app_label}.{model_permission}"):
        return True

    # If not, check object-level permissions
    content_type = ContentType.objects.get_for_model(obj)
    return ObjectPermission.objects.filter(
        user=user, action=action, content_type=content_type, object_id=obj.pk
    ).exists()


def grant_object_permission(user, obj, action):
    """Grant a user permission to perform an action on an object."""
    content_type = ContentType.objects.get_for_model(obj)
    ObjectPermission.objects.get_or_create(
        user=user, action=action, content_type=content_type, object_id=obj.pk
    )


def revoke_object_permission(user, obj, action):
    """Revoke a user's permission to perform an action on an object."""
    content_type = ContentType.objects.get_for_model(obj)
    ObjectPermission.objects.filter(
        user=user, action=action, content_type=content_type, object_id=obj.pk
    ).delete()


def grant_group_permission(group, model_class, action):
    """Grant a group permission to perform an action on a model."""
    content_type = ContentType.objects.get_for_model(model_class)
    permission = Permission.objects.get(
        content_type=content_type, codename=f"{action}_{model_class._meta.model_name}"
    )
    group.permissions.add(permission)


def revoke_group_permission(group, model_class, action):
    """Revoke a group's permission to perform an action on a model."""
    content_type = ContentType.objects.get_for_model(model_class)
    permission = Permission.objects.get(
        content_type=content_type, codename=f"{action}_{model_class._meta.model_name}"
    )
    group.permissions.remove(permission)


def get_permitted_objects(user, action, model_class):
    """Get all objects of a given model that a user has permission to perform an action on."""
    # Get objects through model-level permissions
    model_permission = f"{action}_{model_class._meta.model_name}"
    if user.has_perm(f"{model_class._meta.app_label}.{model_permission}"):
        return model_class.objects.all()

    # Get objects through object-level permissions
    content_type = ContentType.objects.get_for_model(model_class)
    permission_ids = ObjectPermission.objects.filter(
        user=user, action=action, content_type=content_type
    ).values_list("object_id", flat=True)
    return model_class.objects.filter(id__in=permission_ids)


def get_permitted_object(user, action, model_class, object_id):
    """Get an object of a given model that a user has permission to perform an action on."""
    try:
        obj = model_class.objects.get(id=object_id)
    except model_class.DoesNotExist:
        raise Http404

    if not can(user, action, obj):
        raise PermissionDenied

    return obj
