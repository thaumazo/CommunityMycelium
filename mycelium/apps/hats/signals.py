from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.conf import settings
from .models import Hat
from apps.acl.utils import grant_object_permission, revoke_object_permission
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


@receiver(post_save, sender=Hat)
def grant_hat_creator_permissions(sender, instance, created, **kwargs):
    """Grant all permissions to the hat creator when the hat is created."""
    if created and instance.created_by:
        # Get all permissions for Hat model
        hat_permissions = Permission.objects.filter(
            content_type=ContentType.objects.get_for_model(Hat)
        )
        for permission in hat_permissions:
            # Extract the base action from the permission codename (e.g., "add_hat" -> "add")
            base_action = permission.codename.split("_")[0]
            grant_object_permission(instance.created_by, instance, base_action)


@receiver(pre_delete, sender=Hat)
def delete_hat_permissions(sender, instance, **kwargs):
    """Delete all permissions for a hat when it is deleted."""
    # Get all permissions for this hat and delete them
    for permission in instance.permissions.all():
        revoke_object_permission(permission.user, instance, permission.action)
