from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.communities.models import Resolution
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Sets up resolution-specific roles and permissions"

    def handle(self, *args, **options):
        # Create resolution-specific groups
        resolution_admin_group, _ = Group.objects.get_or_create(name="Resolutions Admin")
        resolution_editor_group, _ = Group.objects.get_or_create(name="Resolutions Editor")
        resolution_viewer_group, _ = Group.objects.get_or_create(name="Resolutions Viewer")

        # Get content type for Resolution model
        resolution_content_type = ContentType.objects.get_for_model(Resolution)

        # Get all permissions for Resolution model
        resolution_permissions = Permission.objects.filter(
            content_type=resolution_content_type
        )

        # Resolutions admin group gets all permissions for resolutions
        resolutions_admin_permissions = resolution_permissions.filter(
            codename__in=[
                "add_resolution",
                "change_resolution",
                "delete_resolution",
                "view_resolution",
                "delegate_resolution",
            ]
        )
        resolutions_admin_group.permissions.set(resolutions_admin_permissions)

        # Resolution editor group gets view_resolution permission
        resolutions_editor_permissions = resolution_permissions.filter(
            codename__in=[
                "add_resolution",
                "view_resolution",
            ]
        )
        resolutions_editor_group.permissions.set(resolutions_editor_permissions)

        # Resolutions viewer group gets view_resolution permission
        resolutions_viewer_permissions = resolution_permissions.filter(
            codename__in=[
                "view_resolution",
            ]
        )
        resolutions_viewer_group.permissions.set(resolutions_viewer_permissions)

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully set up resolution-specific roles and permissions"
            )
        )
