from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.agreements.models import Agreement
from apps.communities.models import Community
from apps.hats.models import Hat
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
        agreement_content_type = ContentType.objects.get_for_model(Agreement)
        community_content_type = ContentType.objects.get_for_model(Community)
        hat_content_type = ContentType.objects.get_for_model(Hat)
        meeting_content_type = ContentType.objects.get_for_model(Meeting)
        project_content_type = ContentType.objects.get_for_model(Project)
        task_content_type = ContentType.objects.get_for_model(Task)
        user_content_type = ContentType.objects.get_for_model(User)

        # Get all permissions
        agreement_permissions = Permission.objects.filter(
            content_type=agreement_content_type
        )
        community_permissions = Permission.objects.filter(
            content_type=community_content_type
        )
        hat_permissions = Permission.objects.filter(content_type=hat_content_type)
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
            agreement_permissions.filter(
                codename__in=[
                    "add_agreement",
                    "change_agreement",
                    "delete_agreement",
                    "view_agreement",
                    "delegate_agreement",
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
            | hat_permissions.filter(
                codename__in=[
                    "add_hat",
                    "change_hat",
                    "delete_hat",
                    "view_hat",
                    "delegate_hat",
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
