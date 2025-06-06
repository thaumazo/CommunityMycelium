from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from .models import ObjectPermission
from .forms import ObjectPermissionForm, UserSelectForm
from .utils import (
    get_permitted_content_types,
    get_permitted_objects,
    get_permitted_object,
)

User = get_user_model()


@login_required
def content_type_list_view(request):
    """List all object types in the database for which this user has group or object delegate permissions."""
    # Get all content types that the user has delegate permissions for
    content_types_with_counts = get_permitted_content_types(request.user, "delegate")

    # Create a list of tuples containing each content type and its object count
    content_type_info = []
    for content_type in content_types_with_counts:
        # Get the model class for this content type
        model_class = content_type.model_class()
        # Count the number of objects that the user
        # has delegate permissions for either through
        # model-level permissions or object-level permissions
        object_count = len(get_permitted_objects(request.user, "delegate", model_class))
        # Add the content type and its count to our list
        content_type_info.append((content_type, object_count))

    return render(
        request,
        "acl/content_type_list.html",
        {"content_types_with_counts": content_type_info},
    )


@login_required
def object_list_view(request, content_type_id):
    """List all objects of a specific type for which this user has object delegate permissions."""
    # Get the content type for this object list
    content_type = get_object_or_404(ContentType, id=content_type_id)
    # Get the model class for this content type
    model_class = content_type.model_class()
    # Get all objects of this model that user
    # has delegate permissions for either through
    # model-level permissions or object-level permissions
    objects = get_permitted_objects(request.user, "delegate", model_class)

    return render(
        request,
        "acl/object_list.html",
        {"objects": objects, "content_type": content_type},
    )


@login_required
def object_user_permission_list_view(request, content_type_id, object_id):
    """Edit permissions for a any given object."""
    content_type = get_object_or_404(ContentType, id=content_type_id)
    model_class = content_type.model_class()
    object = get_permitted_object(request.user, "delegate", model_class, object_id)

    if request.method == "POST":
        form = UserSelectForm(request.POST)
        if form.is_valid():
            return redirect(
                "object_user_permission_form",
                content_type_id=content_type_id,
                object_id=object_id,
                user_id=form.cleaned_data["user"].id,
            )
    else:
        form = UserSelectForm()

    return render(
        request,
        "acl/object_user_permission_list.html",
        {"form": form, "object": object},
    )


@login_required
def object_user_permission_form_view(request, content_type_id, object_id, user_id):
    """Edit the permissions for a specific user on a specific object."""
    user = get_object_or_404(User, id=user_id)
    content_type = get_object_or_404(ContentType, id=content_type_id)
    model_class = content_type.model_class()
    object = get_permitted_object(request.user, "delegate", model_class, object_id)

    # Get existing object-level permissions for this user on this object
    existing_object_permissions = object.permissions.filter(user=user)

    # Get group-level permissions
    group_permissions = []
    for group in user.groups.all():
        for permission in group.permissions.all():
            if (
                permission.content_type == content_type
                and permission.codename.startswith(
                    ("add_", "change_", "delete_", "view_", "delegate_")
                )
            ):
                action = permission.codename.split("_")[0]
                if action not in group_permissions:
                    group_permissions.append(action)

    initial_data = {
        "user": user.id,
        "content_type": content_type.id,
        "object_id": object.id,
    }

    if request.method == "POST":
        form = ObjectPermissionForm(request.POST, initial=initial_data)
        if form.is_valid():
            # Delete existing object-level permissions for this user on this object
            existing_object_permissions.delete()
            # Create new permissions
            for action in form.cleaned_data["actions"]:
                ObjectPermission.objects.create(
                    user=user,
                    content_type=content_type,
                    object_id=object.id,
                    action=action,
                )
            messages.success(request, "Permissions updated successfully!")
            return redirect(
                "object_user_permission_list",
                content_type_id=content_type_id,
                object_id=object_id,
            )
    else:
        # Pre-select existing object-level permissions
        initial_data["actions"] = [p.action for p in existing_object_permissions]
        form = ObjectPermissionForm(initial=initial_data)

    return render(
        request,
        "acl/object_user_permission_form.html",
        {
            "form": form,
            "object": object,
            "user": user,
            "content_type": content_type,
            "existing_object_permissions": existing_object_permissions,
            "group_permissions": group_permissions,
        },
    )
