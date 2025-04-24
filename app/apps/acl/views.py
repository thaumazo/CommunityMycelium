from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from .models import ObjectPermission
from .forms import ObjectPermissionForm

User = get_user_model()


@login_required
def content_type_list_view(request):
    """List all object types in the database for which this user has object write permissions."""

    content_types = ContentType.objects.filter(
        objectpermission__user=request.user, objectpermission__action="write"
    ).distinct()

    # Get counts for each content type where user has write permissions
    content_types_with_counts = []
    for content_type in content_types:
        model_class = content_type.model_class()
        count = model_class.objects.filter(
            permissions__user=request.user, permissions__action="write"
        ).count()
        content_types_with_counts.append((content_type, count))

    return render(
        request,
        "acl/content_type_list.html",
        {"content_types_with_counts": content_types_with_counts},
    )


@login_required
def object_list_view(request, content_type_id):
    """List all objects of a specific type for which this user has object write permissions."""

    content_type = get_object_or_404(ContentType, id=content_type_id)
    model_class = content_type.model_class()

    objects = model_class.objects.filter(
        permissions__user=request.user, permissions__action="write"
    )

    return render(
        request,
        "acl/object_list.html",
        {"objects": objects, "content_type": content_type},
    )


@login_required
def object_user_permission_detail_view(request, content_type_id, object_id):
    """Display details of a specific object."""
    content_type = get_object_or_404(ContentType, id=content_type_id)
    model_class = content_type.model_class()
    object = get_object_or_404(model_class, id=object_id)

    # Get all users along with their permissions for this object
    users = User.objects.all()
    users_with_permissions = {}

    for user in users:
        user_permissions = object.permissions.filter(user=user)
        users_with_permissions[user] = [
            permission.action for permission in user_permissions
        ]

    return render(
        request,
        "acl/object_user_permission_detail.html",
        {
            "object": object,
            "content_type": content_type,
            "users_with_permissions": users_with_permissions.items(),
        },
    )


@login_required
def object_user_permission_form_view(request, content_type_id, object_id, user_id):
    """Edit the permissions for a specific user on a specific object."""
    content_type = get_object_or_404(ContentType, id=content_type_id)
    model_class = content_type.model_class()
    object = get_object_or_404(model_class, id=object_id)
    user = get_object_or_404(User, id=user_id)

    # Get existing permissions for this user on this object
    existing_permissions = object.permissions.filter(user=user)
    initial_data = {
        "user": user.id,
        "content_type": content_type.id,
        "object_id": object.id,
    }

    if request.method == "POST":
        form = ObjectPermissionForm(request.POST, initial=initial_data)
        if form.is_valid():
            # Delete existing permissions for this user on this object
            existing_permissions.delete()
            # Create new permissions
            for action in form.cleaned_data["actions"]:
                ObjectPermission.objects.create(
                    user=user,
                    content_type=content_type,
                    object_id=object.id,
                    action=action,
                )
            return redirect(
                "object_user_permission_detail",
                content_type_id=content_type_id,
                object_id=object_id,
            )
    else:
        # Pre-select existing permissions
        initial_data["actions"] = [p.action for p in existing_permissions]
        form = ObjectPermissionForm(initial=initial_data)

    return render(
        request,
        "acl/object_user_permission_form.html",
        {
            "form": form,
            "object": object,
            "user": user,
            "content_type": content_type,
            "existing_permissions": existing_permissions,
        },
    )
