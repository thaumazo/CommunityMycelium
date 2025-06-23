from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.conf import settings
from .models import Agreement
from apps.acl.utils import grant_object_permission, revoke_object_permission
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


@receiver(post_save, sender=Agreement)
def grant_agreement_creator_permissions(sender, instance, created, **kwargs):
    """Grant all permissions to the agreement creator when the agreement is created."""
    if created and instance.created_by:
        # Get all permissions for Agreement model
        agreement_permissions = Permission.objects.filter(
            content_type=ContentType.objects.get_for_model(Agreement)
        )
        for permission in agreement_permissions:
            # Extract the base action from the permission codename (e.g., "add_agreement" -> "add")
            base_action = permission.codename.split("_")[0]
            grant_object_permission(instance.created_by, instance, base_action)


@receiver(pre_delete, sender=Agreement)
def delete_agreement_permissions(sender, instance, **kwargs):
    """Delete all permissions for an agreement when it is deleted."""
    # Get all permissions for this agreement and delete them
    for permission in instance.permissions.all():
        revoke_object_permission(permission.user, instance, permission.action)
