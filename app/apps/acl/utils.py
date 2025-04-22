from django.contrib.contenttypes.models import ContentType
from .models import ObjectPermission


def can(user, action, obj):
    """Check if a user has permission to perform `action` on `obj`."""
    content_type = ContentType.objects.get_for_model(obj)
    return ObjectPermission.objects.filter(
        user=user, action=action, content_type=content_type, object_id=obj.pk
    ).exists()


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


# Get all objects with permission
def get_objects_with_permission(user, action, model_class):
    """Get all objects of a given model that a user has permission to perform an action on."""
    content_type = ContentType.objects.get_for_model(model_class)
    permission_ids = ObjectPermission.objects.filter(
        user=user, action=action, content_type=content_type
    ).values_list("object_id", flat=True)

    return model_class.objects.filter(id__in=permission_ids)
