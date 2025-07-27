from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Socialrole
from apps.acl.utils import grant_object_permission, revoke_object_permission
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


@receiver(post_save, sender=Socialrole)
def grant_socialrole_creator_permissions(sender, instance, created, **kwargs):
    """Grant all permissions to the socialrole creator when the socialrole is created."""
    if created and instance.created_by:
        # Get all permissions for Socialrole model
        socialrole_permissions = Permission.objects.filter(
            content_type=ContentType.objects.get_for_model(Socialrole)
        )
        for permission in socialrole_permissions:
            # Extract the base action from the permission codename (e.g., "add_socialrole" -> "add")
            base_action = permission.codename.split("_")[0]
            grant_object_permission(instance.created_by, instance, base_action)


@receiver(pre_delete, sender=Socialrole)
def delete_socialrole_permissions(sender, instance, **kwargs):
    """Delete all permissions for a socialrole when it is deleted."""
    # Get all permissions for this socialrole and delete them
    for permission in instance.permissions.all():
        revoke_object_permission(permission.user, instance, permission.action)
