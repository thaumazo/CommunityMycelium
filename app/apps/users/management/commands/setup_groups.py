from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.meetings.models import Meeting


class Command(BaseCommand):
    help = "Sets up initial groups and permissions"

    def handle(self, *args, **options):
        # Create groups
        admin_group, _ = Group.objects.get_or_create(name="Admin")
        editor_group, _ = Group.objects.get_or_create(name="Editor")
        viewer_group, _ = Group.objects.get_or_create(name="Viewer")

        # Get content type for Meeting model
        meeting_content_type = ContentType.objects.get_for_model(Meeting)

        # Get all permissions for Meeting model
        meeting_permissions = Permission.objects.filter(
            content_type=meeting_content_type
        )

        # Assign permissions to groups
        # Admin gets all permissions including delegate
        admin_permissions = meeting_permissions.filter(
            codename__in=[
                "add_meeting",
                "change_meeting",
                "delete_meeting",
                "view_meeting",
                "delegate_meeting",  # Permission to manage other users' permissions
            ]
        )
        admin_group.permissions.set(admin_permissions)

        # Editor gets add, change, and view permissions
        editor_permissions = meeting_permissions.filter(
            codename__in=["add_meeting", "change_meeting", "view_meeting"]
        )
        editor_group.permissions.set(editor_permissions)

        # Viewer only gets view permission
        viewer_permissions = meeting_permissions.filter(codename="view_meeting")
        viewer_group.permissions.set(viewer_permissions)

        self.stdout.write(
            self.style.SUCCESS("Successfully set up groups and permissions")
        )
