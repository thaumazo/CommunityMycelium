from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Project
from apps.acl.utils import grant_object_permission, revoke_object_permission
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


@receiver(post_save, sender=Project)
def grant_project_creator_permissions(sender, instance, created, **kwargs):
    """Grant all permissions to the project creator when the project is created."""
    if created and instance.created_by:
        # Get all permissions for Project model
        project_permissions = Permission.objects.filter(
            content_type=ContentType.objects.get_for_model(Project)
        )
        for permission in project_permissions:
            # Extract the base action from the permission codename (e.g., "add_project" -> "add")
            base_action = permission.codename.split("_")[0]
            grant_object_permission(instance.created_by, instance, base_action)


@receiver(pre_delete, sender=Project)
def delete_project_permissions(sender, instance, **kwargs):
    """Delete all permissions for a project when it is deleted."""
    # Get all permissions for this project and delete them
    for permission in instance.permissions.all():
        revoke_object_permission(permission.user, instance, permission.action)
