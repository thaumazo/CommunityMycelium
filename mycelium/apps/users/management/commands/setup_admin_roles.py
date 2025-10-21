from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.resolutions.models import Resolution
from apps.communities.models import Community
from apps.relationships.models import Relationship
from apps.meetings.models import Meeting
from apps.projects.models import Project
from apps.tasks.models import Task
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Sets up admin-specific roles and permissions"

    def handle(self, *args, **options):
        # Create admin group
        admin_group, _ = Group.objects.get_or_create(name="Admin")

        # Get content types
        resolution_content_type = ContentType.objects.get_for_model(Resolution)
        community_content_type = ContentType.objects.get_for_model(Community)
        relationship_content_type = ContentType.objects.get_for_model(Relationship)
        meeting_content_type = ContentType.objects.get_for_model(Meeting)
        project_content_type = ContentType.objects.get_for_model(Project)
        task_content_type = ContentType.objects.get_for_model(Task)
        user_content_type = ContentType.objects.get_for_model(User)

        # Get all permissions
        resolution_permissions = Permission.objects.filter(
            content_type=resolution_content_type
        )
        community_permissions = Permission.objects.filter(
            content_type=community_content_type
        )
        relationship_permissions = Permission.objects.filter(content_type=relationship_content_type)
        meeting_permissions = Permission.objects.filter(
            content_type=meeting_content_type
        )
        project_permissions = Permission.objects.filter(
            content_type=project_content_type
        )
        task_permissions = Permission.objects.filter(content_type=task_content_type)
        user_permissions = Permission.objects.filter(content_type=user_content_type)

        # Assign permissions to admin group
        # Admin gets all permissions for both users and meetings
        admin_permissions = (
            resolution_permissions.filter(
                codename__in=[
                    "add_resolution",
                    "change_resolution",
                    "delete_resolution",
                    "view_resolution",
                    "delegate_resolution",
                ]
            )
            | community_permissions.filter(
                codename__in=[
                    "add_community",
                    "change_community",
                    "delete_community",
                    "view_community",
                    "delegate_community",
                ]
            )
            | relationship_permissions.filter(
                codename__in=[
                    "add_relationship",
                    "change_relationship",
                    "delete_relationship",
                    "view_relationship",
                    "delegate_relationship",
                ]
            )
            | meeting_permissions.filter(
                codename__in=[
                    "add_meeting",
                    "change_meeting",
                    "delete_meeting",
                    "view_meeting",
                    "delegate_meeting",
                ]
            )
            | project_permissions.filter(
                codename__in=[
                    "add_project",
                    "change_project",
                    "delete_project",
                    "view_project",
                    "delegate_project",
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
