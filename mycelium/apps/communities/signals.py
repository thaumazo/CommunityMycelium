from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.conf import settings
from .models import Community
from apps.acl.utils import grant_object_permission, revoke_object_permission
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


@receiver(post_save, sender=Community)
def grant_community_creator_permissions(sender, instance, created, **kwargs):
    """Grant all permissions to the community creator when the community is created."""
    if created and instance.created_by:
        # Get all permissions for Community model
        community_permissions = Permission.objects.filter(
            content_type=ContentType.objects.get_for_model(Community)
        )
        for permission in community_permissions:
            # Extract the base action from the permission codename (e.g., "add_community" -> "add")
            base_action = permission.codename.split("_")[0]
            grant_object_permission(instance.created_by, instance, base_action)


@receiver(pre_delete, sender=Community)
def delete_community_permissions(sender, instance, **kwargs):
    """Delete all permissions for a community when it is deleted."""
    # Get all permissions for this community and delete them
    for permission in instance.permissions.all():
        revoke_object_permission(permission.user, instance, permission.action)
