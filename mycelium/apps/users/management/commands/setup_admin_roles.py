from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.meetings.models import Meeting
from apps.tasks.models import Task
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Sets up admin-specific roles and permissions"

    def handle(self, *args, **options):
        # Create admin group
        admin_group, _ = Group.objects.get_or_create(name="Admin")

        # Get content types for Meeting and User models
        meeting_content_type = ContentType.objects.get_for_model(Meeting)
        task_content_type = ContentType.objects.get_for_model(Task)
        user_content_type = ContentType.objects.get_for_model(User)

        # Get all permissions for Meeting and User models
        meeting_permissions = Permission.objects.filter(
            content_type=meeting_content_type
        )
        task_permissions = Permission.objects.filter(content_type=task_content_type)
        user_permissions = Permission.objects.filter(content_type=user_content_type)

        # Assign permissions to admin group
        # Admin gets all permissions for both users and meetings
        admin_permissions = (
            meeting_permissions.filter(
                codename__in=[
                    "add_meeting",
                    "change_meeting",
                    "delete_meeting",
                    "view_meeting",
                    "delegate_meeting",
                ]
            )
            | task_permissions.filter(
                codename__in=[
                    "add_task",
                    "change_task",
                    "delete_task",
                    "view_task",
                    "delegate_task",
                ]
            )
            | user_permissions.filter(
                codename__in=[
                    "add_user",
                    "change_user",
                    "delete_user",
                    "view_user",
                ]
            )
        )
        admin_group.permissions.set(admin_permissions)

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully set up admin-specific roles and permissions"
            )
        )
