from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Socialrole
from apps.acl.utils import revoke_object_permission
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


@receiver(post_save, sender=Socialrole)
def grant_socialrole_creator_permissions(sender, instance, created, **kwargs):
    """Stub: no-op since Socialroles are system-defined and do not have a creator."""
    pass  # Remove or replace this with a different permission logic if needed


@receiver(pre_delete, sender=Socialrole)
def delete_socialrole_permissions(sender, instance, **kwargs):
    """Delete all permissions for a socialrole when it is deleted."""
    for permission in instance.permissions.all():
        revoke_object_permission(permission.user, instance, permission.action)
