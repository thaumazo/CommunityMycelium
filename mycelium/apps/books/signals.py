from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Book
from apps.acl.utils import grant_object_permission, revoke_object_permission
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


@receiver(post_save, sender=Book)
def grant_book_creator_permissions(sender, instance, created, **kwargs):
    """Grant all permissions to the book creator when the book is created."""
    if created and instance.created_by:
        # Get all permissions for Book model
        book_permissions = Permission.objects.filter(
            content_type=ContentType.objects.get_for_model(Book)
        )
        for permission in book_permissions:
            # Extract the base action from the permission codename (e.g., "add_book" -> "add")
            base_action = permission.codename.split("_")[0]
            grant_object_permission(instance.created_by, instance, base_action)


@receiver(pre_delete, sender=Book)
def delete_book_permissions(sender, instance, **kwargs):
    """Delete all permissions for a book when it is deleted."""
    # Get all permissions for this book and delete them
    for permission in instance.permissions.all():
        revoke_object_permission(permission.user, instance, permission.action)
