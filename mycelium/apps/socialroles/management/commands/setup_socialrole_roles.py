from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.communities.models import Socialrole
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Sets up socialrole-specific roles and permissions"

    def handle(self, *args, **options):
        # Create socialrole-specific groups
        socialroles_admin_group, _ = Group.objects.get_or_create(name="Social Roles Admin")
        socialroles_editor_group, _ = Group.objects.get_or_create(name="Social Roles Editor")
        socialroles_viewer_group, _ = Group.objects.get_or_create(name="Social Roles Viewer")

        # Get content type for Social Role model
        socialrole_content_type = ContentType.objects.get_for_model(Socialrole)

        # Get all permissions for Social Role model
        socialrole_permissions = Permission.objects.filter(
            content_type=socialrole_content_type
        )

        # Social Roles admin group gets all permissions for social roles
        socialroles_admin_permissions = socialrole_permissions.filter(
            codename__in=[
                "add_socialrole",
                "change_socialrole",
                "delete_socialrole",
                "view_socialrole",
                "delegate_socialrole",
            ]
        )
        socialroles_admin_group.permissions.set(socialroles_admin_permissions)

        # Social Roles editor group gets view_socialrole permission
        socialroles_editor_permissions = socialrole_permissions.filter(
            codename__in=[
                "add_socialrole",
                "view_socialrole",
            ]
        )
        socialroles_editor_group.permissions.set(socialroles_editor_permissions)

        # Social Roles viewer group gets view_socialrole permission
        socialroles_viewer_permissions = socialrole_permissions.filter(
            codename__in=[
                "view_socialrole",
            ]
        )
        socialroles_viewer_group.permissions.set(socialroles_viewer_permissions)

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully set up socialrole-specific roles and permissions"
            )
        )
