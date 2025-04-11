from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.meetings.models import Meeting
from apps.users.models import User


class Command(BaseCommand):
    help = "Sets up initial user groups and permissions"

    def handle(self, *args, **options):
        # Create groups
        viewer_group, _ = Group.objects.get_or_create(name="viewer")
        editor_group, _ = Group.objects.get_or_create(name="editor")
        admin_group, _ = Group.objects.get_or_create(name="admin")

        # Get content types
        meeting_content_type = ContentType.objects.get_for_model(Meeting)
        user_content_type = ContentType.objects.get_for_model(User)

        # Clear existing permissions
        viewer_group.permissions.clear()
        editor_group.permissions.clear()
        admin_group.permissions.clear()

        # Get meeting permissions
        view_meeting_perm = Permission.objects.get(
            codename="view_meeting", content_type=meeting_content_type
        )
        add_meeting_perm = Permission.objects.get(
            codename="add_meeting", content_type=meeting_content_type
        )
        change_meeting_perm = Permission.objects.get(
            codename="change_meeting", content_type=meeting_content_type
        )
        delete_meeting_perm = Permission.objects.get(
            codename="delete_meeting", content_type=meeting_content_type
        )

        # Get user permissions
        view_user_perm = Permission.objects.get(
            codename="view_user", content_type=user_content_type
        )
        add_user_perm = Permission.objects.get(
            codename="add_user", content_type=user_content_type
        )
        change_user_perm = Permission.objects.get(
            codename="change_user", content_type=user_content_type
        )
        delete_user_perm = Permission.objects.get(
            codename="delete_user", content_type=user_content_type
        )

        # Assign permissions to groups
        # Viewer group - can view meetings and users
        viewer_group.permissions.add(view_meeting_perm, view_user_perm)

        # Editor group - can view, add, and change meetings and users
        editor_group.permissions.add(
            view_meeting_perm,
            add_meeting_perm,
            change_meeting_perm,
            view_user_perm,
            add_user_perm,
            change_user_perm,
        )

        # Admin group - can do everything
        admin_group.permissions.add(
            view_meeting_perm,
            add_meeting_perm,
            change_meeting_perm,
            delete_meeting_perm,
            view_user_perm,
            add_user_perm,
            change_user_perm,
            delete_user_perm,
        )

        # Debug output
        self.stdout.write("\nPermissions assigned:")
        for group in [viewer_group, editor_group, admin_group]:
            self.stdout.write(f"\n{group.name} group permissions:")
            for perm in group.permissions.all():
                self.stdout.write(f"  - {perm.content_type.app_label}.{perm.codename}")

        self.stdout.write(
            self.style.SUCCESS("\nSuccessfully set up groups and permissions")
        )
