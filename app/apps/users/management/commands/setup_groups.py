from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.meetings.models import Meeting
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Sets up initial groups and permissions"

    def handle(self, *args, **options):
        # Create groups
        admin_group, _ = Group.objects.get_or_create(name="Admin")
        editor_group, _ = Group.objects.get_or_create(name="Editor")
        viewer_group, _ = Group.objects.get_or_create(name="Viewer")

        # Get content types for Meeting and User models
        meeting_content_type = ContentType.objects.get_for_model(Meeting)
        user_content_type = ContentType.objects.get_for_model(User)

        # Get all permissions for Meeting and User models
        meeting_permissions = Permission.objects.filter(
            content_type=meeting_content_type
        )
        user_permissions = Permission.objects.filter(content_type=user_content_type)

        # Assign permissions to groups
        # Admin gets all permissions for both users and meetings
        admin_permissions = meeting_permissions.filter(
            codename__in=[
                "add_meeting",
                "change_meeting",
                "delete_meeting",
                "view_meeting",
                "delegate_meeting",
            ]
        ) | user_permissions.filter(
            codename__in=[
                "add_user",
                "change_user",
                "delete_user",
                "view_user",
            ]
        )
        admin_group.permissions.set(admin_permissions)

        # Editor gets view permission for users and all permissions for meetings
        editor_permissions = meeting_permissions.filter(
            codename__in=["add_meeting", "change_meeting", "view_meeting"]
        ) | user_permissions.filter(codename="view_user")
        editor_group.permissions.set(editor_permissions)

        # Viewer gets view permission for both users and meetings
        viewer_permissions = meeting_permissions.filter(
            codename="view_meeting"
        ) | user_permissions.filter(codename="view_user")
        viewer_group.permissions.set(viewer_permissions)

        self.stdout.write(
            self.style.SUCCESS("Successfully set up groups and permissions")
        )
