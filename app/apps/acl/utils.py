from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.http import Http404
from .models import ObjectPermission


def grant_permission(user, obj, action):
    content_type = ContentType.objects.get_for_model(obj)
    ObjectPermission.objects.get_or_create(
        user=user, action=action, content_type=content_type, object_id=obj.pk
    )


def revoke_permission(user, obj, action):
    content_type = ContentType.objects.get_for_model(obj)
    ObjectPermission.objects.filter(
        user=user, action=action, content_type=content_type, object_id=obj.pk
    ).delete()


def can(user, action, obj):
    """Check if a user has permission to perform `action` on `obj`."""

    # Get the content type of the object
    content_type = ContentType.objects.get_for_model(obj)

    # Check if the user has permission to perform the action on the object
    return ObjectPermission.objects.filter(
        user=user, action=action, content_type=content_type, object_id=obj.pk
    ).exists()


def get_permitted_objects(user, action, model_class):
    """Get all objects of a given model that a user has permission to perform an action on."""

    # Get the content type of the model
    content_type = ContentType.objects.get_for_model(model_class)

    # Get the object ids of the objects that the user has permission to perform the action on
    permission_ids = ObjectPermission.objects.filter(
        user=user, action=action, content_type=content_type
    ).values_list("object_id", flat=True)

    # Return the objects
    return model_class.objects.filter(id__in=permission_ids)


def get_permitted_object(user, action, model_class, object_id):
    """Get an object of a given model that a user has permission to perform an action on."""

    # Get the object or raise a 404 if it does not exist
    try:
        object = model_class.objects.get(id=object_id)
    except model_class.DoesNotExist:
        raise Http404

    # Check if the user has permission to perform the action on the object
    if not can(user, action, object):
        raise PermissionDenied

    # Return the object
    return object
