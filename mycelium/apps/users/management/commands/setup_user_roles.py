from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.users.models import User


class Command(BaseCommand):
    help = "Sets up user-specific roles and permissions"

    def handle(self, *args, **options):
        # Create User Admin group
        user_admin_group, _ = Group.objects.get_or_create(name="User Admin")

        # Create User Viewer group
        user_viewer_group, _ = Group.objects.get_or_create(name="User Viewer")

        # Get content type for User model
        user_content_type = ContentType.objects.get_for_model(User)

        # Get all permissions for User model
        user_permissions = Permission.objects.filter(content_type=user_content_type)

        # Users admin group gets all permissions for users
        user_admin_permissions = user_permissions.filter(
            codename__in=[
                "add_user",
                "change_user",
                "delete_user",
                "view_user",
            ]
        )
        user_admin_group.permissions.set(user_admin_permissions)
        self.stdout.write(
            self.style.SUCCESS(
                f'Assigned {user_admin_permissions.count()} permissions to "User Admin" group'
            )
        )

        # Users viewer group gets view_user permission
        user_viewer_permissions = user_permissions.filter(
            codename__in=[
                "view_user",
            ]
        )
        user_viewer_group.permissions.set(user_viewer_permissions)
        self.stdout.write(
            self.style.SUCCESS(
                f'Assigned {user_viewer_permissions.count()} permissions to "User Viewer" group'
            )
        )
