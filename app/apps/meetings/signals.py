from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.conf import settings
from .models import Meeting
from apps.acl.utils import grant_permission, revoke_permission


@receiver(post_save, sender=Meeting)
def grant_meeting_creator_permissions(sender, instance, created, **kwargs):
    if created and instance.created_by:
        grant_permission(instance.created_by, instance, "read")
        grant_permission(instance.created_by, instance, "write")


@receiver(pre_delete, sender=Meeting)
def revoke_meeting_permissions(sender, instance, **kwargs):
    # Get all permissions for this meeting and delete them
    for permission in instance.permissions.all():
        revoke_permission(permission.user, instance, permission.action)
