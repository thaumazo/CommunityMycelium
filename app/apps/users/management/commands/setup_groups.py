from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.meetings.models import Meeting


class Command(BaseCommand):
    help = "Sets up initial user groups and permissions"

    def handle(self, *args, **options):
        # Create groups
        viewer_group, _ = Group.objects.get_or_create(name="viewer")
        editor_group, _ = Group.objects.get_or_create(name="editor")
        admin_group, _ = Group.objects.get_or_create(name="admin")

        # Get content type for Meeting model
        content_type = ContentType.objects.get_for_model(Meeting)

        # Clear existing permissions
        viewer_group.permissions.clear()
        editor_group.permissions.clear()
        admin_group.permissions.clear()

        # Get all relevant permissions
        view_perm = Permission.objects.get(
            codename="view_meeting", content_type=content_type
        )
        add_perm = Permission.objects.get(
            codename="add_meeting", content_type=content_type
        )
        change_perm = Permission.objects.get(
            codename="change_meeting", content_type=content_type
        )
        delete_perm = Permission.objects.get(
            codename="delete_meeting", content_type=content_type
        )

        # Assign permissions to groups
        viewer_group.permissions.add(view_perm)

        editor_group.permissions.add(view_perm, add_perm, change_perm)

        admin_group.permissions.add(view_perm, add_perm, change_perm, delete_perm)

        self.stdout.write(
            self.style.SUCCESS("Successfully set up groups and permissions")
        )
