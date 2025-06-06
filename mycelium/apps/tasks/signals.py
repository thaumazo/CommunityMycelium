from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import Task
from apps.acl.utils import grant_object_permission
from django.contrib.auth.models import Permission


@receiver(post_save, sender=Task)
def grant_task_creator_permissions(sender, instance, created, **kwargs):
    """Grant all permissions to the task creator when the task is created."""
    if created and instance.created_by:
        # Get all permissions for Task model
        task_permissions = Permission.objects.filter(
            content_type=ContentType.objects.get_for_model(Task)
        )
        for permission in task_permissions:
            # Extract the base action from the permission codename (e.g., "add_task" -> "add")
            base_action = permission.codename.split("_")[0]
            grant_object_permission(instance.created_by, instance, base_action)
