from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.communities.models import Hat
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Sets up hat-specific roles and permissions"

    def handle(self, *args, **options):
        # Create hat-specific groups
        hats_admin_group, _ = Group.objects.get_or_create(name="Hats Admin")
        hats_editor_group, _ = Group.objects.get_or_create(name="Hats Editor")
        hats_viewer_group, _ = Group.objects.get_or_create(name="Hats Viewer")

        # Get content type for Hat model
        hat_content_type = ContentType.objects.get_for_model(Hat)

        # Get all permissions for Hat model
        hat_permissions = Permission.objects.filter(
            content_type=hat_content_type
        )

        # Hats admin group gets all permissions for hats
        hats_admin_permissions = hat_permissions.filter(
            codename__in=[
                "add_hat",
                "change_hat",
                "delete_hat",
                "view_hat",
                "delegate_hat",
            ]
        )
        hats_admin_group.permissions.set(hats_admin_permissions)

        # Hats editor group gets view_hat permission
        hats_editor_permissions = hat_permissions.filter(
            codename__in=[
                "add_hat",
                "view_hat",
            ]
        )
        hats_editor_group.permissions.set(hats_editor_permissions)

        # Hats viewer group gets view_hat permission
        hats_viewer_permissions = hat_permissions.filter(
            codename__in=[
                "view_hat",
            ]
        )
        hats_viewer_group.permissions.set(hats_viewer_permissions)

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully set up hat-specific roles and permissions"
            )
        )
