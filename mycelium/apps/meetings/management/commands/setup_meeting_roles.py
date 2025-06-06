from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.meetings.models import Meeting
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Sets up meeting-specific roles and permissions"

    def handle(self, *args, **options):
        # Create meeting-specific groups
        meetings_admin_group, _ = Group.objects.get_or_create(name="Meetings Admin")
        meetings_editor_group, _ = Group.objects.get_or_create(name="Meetings Editor")
        meetings_viewer_group, _ = Group.objects.get_or_create(name="Meetings Viewer")

        # Get content type for Meeting model
        meeting_content_type = ContentType.objects.get_for_model(Meeting)

        # Get all permissions for Meeting model
        meeting_permissions = Permission.objects.filter(
            content_type=meeting_content_type
        )

        # Meetings admin group gets all permissions for meetings
        meetings_admin_permissions = meeting_permissions.filter(
            codename__in=[
                "add_meeting",
                "change_meeting",
                "delete_meeting",
                "view_meeting",
                "delegate_meeting",
            ]
        )
        meetings_admin_group.permissions.set(meetings_admin_permissions)

        # Meetings editor group gets view_meeting permission
        meetings_editor_permissions = meeting_permissions.filter(
            codename__in=[
                "add_meeting",
                "view_meeting",
            ]
        )
        meetings_editor_group.permissions.set(meetings_editor_permissions)

        # Meetings viewer group gets view_meeting permission
        meetings_viewer_permissions = meeting_permissions.filter(
            codename__in=[
                "view_meeting",
            ]
        )
        meetings_viewer_group.permissions.set(meetings_viewer_permissions)

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully set up meeting-specific roles and permissions"
            )
        )
