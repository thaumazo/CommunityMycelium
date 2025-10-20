from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Challenge
from apps.acl.utils import grant_object_permission, revoke_object_permission
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


@receiver(post_save, sender=Challenge)
def grant_challenge_creator_permissions(sender, instance, created, **kwargs):
    """Grant all permissions to the challenge creator when the challenge is created."""
    if created and instance.created_by:
        # Get all permissions for Challenge model
        challenge_permissions = Permission.objects.filter(
            content_type=ContentType.objects.get_for_model(Challenge)
        )
        for permission in challenge_permissions:
            # Extract the base action from the permission codename (e.g., "add_challenge" -> "add")
            base_action = permission.codename.split("_")[0]
            grant_object_permission(instance.created_by, instance, base_action)


@receiver(pre_delete, sender=Challenge)
def delete_challenge_permissions(sender, instance, **kwargs):
    """Delete all permissions for a challenge when it is deleted."""
    # Get all permissions for this challenge and delete them
    for permission in instance.permissions.all():
        revoke_object_permission(permission.user, instance, permission.action)
