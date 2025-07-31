from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.communities.models import Maladaptive
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Sets up maladaptive schema-specific roles and permissions"

    def handle(self, *args, **options):
        # Create maladaptive-specific groups
        maladaptives_admin_group, _ = Group.objects.get_or_create(name="Maladaptive Schema Admin")
        maladaptives_editor_group, _ = Group.objects.get_or_create(name="Maladaptive Schema Editor")
        maladaptives_viewer_group, _ = Group.objects.get_or_create(name="Maladaptive Schema Viewer")

        # Get content type for Maladaptive Schema model
        maladaptive_content_type = ContentType.objects.get_for_model(Maladaptive)

        # Get all permissions for Maladaptive Schema model
        maladaptive_permissions = Permission.objects.filter(
            content_type=maladaptive_content_type
        )

        # Maladaptive Schema admin group gets all permissions for maladaptive schema
        maladaptives_admin_permissions = maladaptive_permissions.filter(
            codename__in=[
                "add_maladaptive",
                "change_maladaptive",
                "delete_maladaptive",
                "view_maladaptive",
                "delegate_maladaptive",
            ]
        )
        maladaptives_admin_group.permissions.set(maladaptives_admin_permissions)

        # Maladaptive Schema editor group gets view_maladaptive permission
        maladaptives_editor_permissions = maladaptive_permissions.filter(
            codename__in=[
                "add_maladaptive",
                "view_maladaptive",
            ]
        )
        maladaptives_editor_group.permissions.set(maladaptives_editor_permissions)

        # Maladaptive Schema viewer group gets view_maladaptive permission
        maladaptives_viewer_permissions = maladaptive_permissions.filter(
            codename__in=[
                "view_maladaptive",
            ]
        )
        maladaptives_viewer_group.permissions.set(maladaptives_viewer_permissions)

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully set up maladaptive-specific roles and permissions"
            )
        )
