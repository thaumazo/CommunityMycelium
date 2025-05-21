from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied
from django.http import Http404
from .models import ObjectPermission


def can(user, action, obj):
    """Check if a user has permission to perform `action` on `obj`."""
    # First, if the object is owned by the user, they can always perform the action
    if hasattr(obj, "created_by") and obj.created_by == user:
        return True

    # If now, check if user has model-level permission through their groups
    model_permission = f"{action}_{obj._meta.model_name}"
    if user.has_perm(f"{obj._meta.app_label}.{model_permission}"):
        return True

    # Finally, check object-level permissions
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


def get_permitted_content_types(user, action):
    """Get all content types that a user has permission to perform an action on."""
    content_types = ContentType.objects.all()

    permitted_content_types = []
    for content_type in content_types:
        # Check if user has model-level permission
        if user.has_perm(
            f"{content_type.app_label}.{action}_{content_type._meta.model_name}"
        ):
            permitted_content_types.append(content_type)
        else:
            # Check if user has object-level permission
            if ObjectPermission.objects.filter(
                user=user, action=action, content_type=content_type
            ).exists():
                permitted_content_types.append(content_type)

    return permitted_content_types


def get_permitted_objects(user, action, model_class):
    """Get all objects of a given model that a user has permission to perform an action on."""
    permitted_objects_by_model_permission = []
    permitted_objects_by_object_permission = []

    # Get objects through model-level permissions
    model_permission = f"{action}_{model_class._meta.model_name}"
    if user.has_perm(f"{model_class._meta.app_label}.{model_permission}"):
        permitted_objects_by_model_permission.extend(model_class.objects.all())

    # Get objects through object-level permissions
    content_type = ContentType.objects.get_for_model(model_class)
    permission_ids = ObjectPermission.objects.filter(
        user=user, action=action, content_type=content_type
    ).values_list("object_id", flat=True)
    permitted_objects_by_object_permission.extend(
        model_class.objects.filter(id__in=permission_ids)
    )

    # Return the union of the two sets
    return list(
        set(permitted_objects_by_model_permission)
        | set(permitted_objects_by_object_permission)
    )


def get_permitted_object(user, action, model_class, object_id):
    """Get an object of a given model that a user has permission to perform an action on."""
    try:
        obj = model_class.objects.get(id=object_id)
    except model_class.DoesNotExist:
        raise Http404

    if not can(user, action, obj):
        raise PermissionDenied

    return obj
