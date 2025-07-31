from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.communities.models import Capital
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Sets up capital schema-specific roles and permissions"

    def handle(self, *args, **options):
        # Create capital-specific groups
        capitals_admin_group, _ = Group.objects.get_or_create(name="Capitals Admin")
        capitals_editor_group, _ = Group.objects.get_or_create(name="Capitals Editor")
        capitals_viewer_group, _ = Group.objects.get_or_create(name="Capitals Viewer")

        # Get content type for Capitals model
        capital_content_type = ContentType.objects.get_for_model(Capital)

        # Get all permissions for Capital model
        capital_permissions = Permission.objects.filter(
            content_type=capital_content_type
        )

        # Capitals admin group gets all permissions for capitals
        capitals_admin_permissions = capital_permissions.filter(
            codename__in=[
                "add_capital",
                "change_capital",
                "delete_capital",
                "view_capital",
                "delegate_capital",
            ]
        )
        capitals_admin_group.permissions.set(capitals_admin_permissions)

        # Capitals editor group gets view_capital permission
        capitals_editor_permissions = capital_permissions.filter(
            codename__in=[
                "add_capital",
                "view_capital",
            ]
        )
        capitals_editor_group.permissions.set(capitals_editor_permissions)

        # Capitals viewer group gets view_capital permission
        capitals_viewer_permissions = capital_permissions.filter(
            codename__in=[
                "view_capital",
            ]
        )
        capitals_viewer_group.permissions.set(capitals_viewer_permissions)

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully set up capital-specific roles and permissions"
            )
        )
