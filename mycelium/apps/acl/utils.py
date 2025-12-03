from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied
from django.http import Http404
from .models import ObjectPermission, ModelPermission
from apps.utils.dump import dump
from apps.users.models import User


def is_permitted(user, action, obj_or_string):
    """
    Check if a user has permission to perform `action` on `obj`.
    
    Permission hierarchy:
    1. Self-permission (user accessing their own User object)
    2. Ownership (user created the object)
    3. Model-level permission via groups (Django's built-in)
    4. Model-level permission via ModelPermission (individual user)
    5. Object-level permission via ObjectPermission (specific object)
    """
    # If the object is a string, it's a model name
    if isinstance(obj_or_string, str):
        # Create a empty object instance of the model
        obj = ContentType.objects.get(
            app_label=obj_or_string.split(".")[0], model=obj_or_string.split(".")[1]
        ).model_class()()
    else:
        obj = obj_or_string

    # If the object is a user, and it's the current user
    if isinstance(obj, User) and obj == user:
        return True
    
    # First, if the object is owned by the user, they can always perform the action
    if hasattr(obj, "created_by") and obj.created_by == user:
        return True

    # Check if user has model-level permission through their groups
    model_permission = f"{action}_{obj._meta.model_name}"
    if user.has_perm(f"{obj._meta.app_label}.{model_permission}"):
        return True

    # Check if user has model-level permission via ModelPermission
    content_type = ContentType.objects.get_for_model(obj)
    if ModelPermission.objects.filter(
        user=user, action=action, content_type=content_type
    ).exists():
        return True

    # Finally, check object-level permissions
    return ObjectPermission.objects.filter(
        user=user, action=action, content_type=content_type, object_id=obj.pk
    ).exists()


def grant_model_permission(user, model_class, action):
    """Grant a user permission to perform an action on all instances of a model."""
    content_type = ContentType.objects.get_for_model(model_class)
    ModelPermission.objects.get_or_create(
        user=user, action=action, content_type=content_type
    )


def revoke_model_permission(user, model_class, action):
    """Revoke a user's permission to perform an action on all instances of a model."""
    content_type = ContentType.objects.get_for_model(model_class)
    ModelPermission.objects.filter(
        user=user, action=action, content_type=content_type
    ).delete()


def grant_object_permission(user, obj, action):
    """Grant a user permission to perform an action on a specific object."""
    content_type = ContentType.objects.get_for_model(obj)
    ObjectPermission.objects.get_or_create(
        user=user, action=action, content_type=content_type, object_id=obj.pk
    )


def revoke_object_permission(user, obj, action):
    """Revoke a user's permission to perform an action on a specific object."""
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
    """
    Get all content types that a user has permission to perform an action on.
    
    Returns content types the user has access to via:
    - Group-based model-level permissions
    - Individual model-level permissions (ModelPermission)
    - Object-level permissions (ObjectPermission)
    """
    content_types = ContentType.objects.all()

    # dump out all the content types
    for content_type in content_types:
        print(
            f"Content type: {content_type} - {content_type.app_label}.{content_type.model} - {content_type.model_class()}",
            flush=True,
        )

    permitted_content_types = []
    for content_type in content_types:
        # Skip content types that don't have a model
        if not content_type.model_class():
            continue

        # if the content type doesn't start with apps (e.g. django.contrib.sessions), skip it
        model_class = content_type.model_class()
        if not model_class.__module__.startswith("apps."):
            continue

        # Check if user has group-based model-level permission
        if user.has_perm(
            f"{content_type.app_label}.{action}_{content_type._meta.model_name}"
        ):
            permitted_content_types.append(content_type)
        # Check if user has individual model-level permission
        elif ModelPermission.objects.filter(
            user=user, action=action, content_type=content_type
        ).exists():
            permitted_content_types.append(content_type)
        # Check if user has object-level permission
        elif ObjectPermission.objects.filter(
            user=user, action=action, content_type=content_type
        ).exists():
            permitted_content_types.append(content_type)

    return permitted_content_types


def get_permitted_objects(user, action, model_class):
    """
    Get all objects of a given model that a user has permission to perform an action on.
    
    Returns objects the user has access to via:
    - Model-level permissions (group-based)
    - Model-level permissions (individual user via ModelPermission)
    - Object-level permissions (specific instances via ObjectPermission)
    """
    permitted_objects_by_model_permission = []
    permitted_objects_by_individual_model_permission = []
    permitted_objects_by_object_permission = []

    # Get objects through group model-level permissions
    model_permission = f"{action}_{model_class._meta.model_name}"
    if user.has_perm(f"{model_class._meta.app_label}.{model_permission}"):
        permitted_objects_by_model_permission.extend(model_class.objects.all())

    # Get objects through individual model-level permissions
    content_type = ContentType.objects.get_for_model(model_class)
    if ModelPermission.objects.filter(
        user=user, action=action, content_type=content_type
    ).exists():
        permitted_objects_by_individual_model_permission.extend(model_class.objects.all())

    # Get objects through object-level permissions
    permission_ids = ObjectPermission.objects.filter(
        user=user, action=action, content_type=content_type
    ).values_list("object_id", flat=True)
    permitted_objects_by_object_permission.extend(
        model_class.objects.filter(id__in=permission_ids)
    )

    # Return the union of all three sets
    return list(
        set(permitted_objects_by_model_permission)
        | set(permitted_objects_by_individual_model_permission)
        | set(permitted_objects_by_object_permission)
    )


def get_permitted_object(user, action, model_class, object_id):
    """Get an object of a given model that a user has permission to perform an action on."""
    try:
        obj = model_class.objects.get(id=object_id)
        content_type = ContentType.objects.get_for_model(model_class)
        obj.content_type = content_type
        obj.foo = "bar"
    except model_class.DoesNotExist:
        raise Http404

    if not is_permitted(user, action, obj):
        raise PermissionDenied

    return obj


def grant_creator_permissions(user, model_class):
    """
    Grant a user permission to:
    - Add new instances of a model
    - View, change, delete, and delegate their own created instances
    
    This is useful for giving users the ability to create and manage their own content.
    Example: grant_creator_permissions(user, Project)
    """
    grant_model_permission(user, model_class, "add")
    # Note: View, change, delete, and delegate permissions for owned objects
    # are automatically granted via the ownership check in is_permitted()


def grant_full_model_access(user, model_class):
    """
    Grant a user full access to all instances of a model.
    Grants: add, view, change, delete, and delegate permissions.
    """
    for action in ["add", "view", "change", "delete", "delegate"]:
        grant_model_permission(user, model_class, action)


def revoke_all_model_permissions(user, model_class):
    """
    Revoke all model-level permissions for a user on a specific model.
    """
    content_type = ContentType.objects.get_for_model(model_class)
    ModelPermission.objects.filter(user=user, content_type=content_type).delete()


def get_user_model_permissions(user, model_class):
    """
    Get all actions a user has model-level permission for on a specific model.
    Returns a list of action strings.
    """
    content_type = ContentType.objects.get_for_model(model_class)
    return list(
        ModelPermission.objects.filter(
            user=user, content_type=content_type
        ).values_list("action", flat=True)
    )
