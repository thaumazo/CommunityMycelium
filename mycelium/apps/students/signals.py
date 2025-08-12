from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Student
from apps.acl.utils import grant_object_permission, revoke_object_permission
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


@receiver(post_save, sender=Student)
def grant_student_creator_permissions(sender, instance, created, **kwargs):
    """Grant all permissions to the student creator when the student is created."""
    if created and instance.created_by:
        # Get all permissions for Student model
        student_permissions = Permission.objects.filter(
            content_type=ContentType.objects.get_for_model(Student)
        )
        for permission in student_permissions:
            # Extract the base action from the permission codename (e.g., "add_student" -> "add")
            base_action = permission.codename.split("_")[0]
            grant_object_permission(instance.created_by, instance, base_action)


@receiver(pre_delete, sender=Student)
def delete_student_permissions(sender, instance, **kwargs):
    """Delete all permissions for a student when it is deleted."""
    # Get all permissions for this student and delete them
    for permission in instance.permissions.all():
        revoke_object_permission(permission.user, instance, permission.action)
