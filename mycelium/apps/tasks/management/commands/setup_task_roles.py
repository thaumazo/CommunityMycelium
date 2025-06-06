from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.tasks.models import Task
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Sets up task-specific roles and permissions"

    def handle(self, *args, **options):
        # Create task-specific groups
        tasks_admin_group, _ = Group.objects.get_or_create(name="Tasks Admin")
        tasks_editor_group, _ = Group.objects.get_or_create(name="Tasks Editor")
        tasks_viewer_group, _ = Group.objects.get_or_create(name="Tasks Viewer")

        # Get content type for Task model
        task_content_type = ContentType.objects.get_for_model(Task)

        # Get all permissions for Task model
        task_permissions = Permission.objects.filter(content_type=task_content_type)

        # Tasks admin group gets all permissions for tasks
        tasks_admin_permissions = task_permissions.filter(
            codename__in=[
                "add_task",
                "change_task",
                "delete_task",
                "view_task",
                "delegate_task",
            ]
        )
        tasks_admin_group.permissions.set(tasks_admin_permissions)

        # Tasks editor group gets add_task and view_task permissions
        tasks_editor_permissions = task_permissions.filter(
            codename__in=[
                "add_task",
                "view_task",
            ]
        )
        tasks_editor_group.permissions.set(tasks_editor_permissions)

        # Tasks viewer group gets view_task permission
        tasks_viewer_permissions = task_permissions.filter(
            codename__in=[
                "view_task",
            ]
        )
        tasks_viewer_group.permissions.set(tasks_viewer_permissions)
