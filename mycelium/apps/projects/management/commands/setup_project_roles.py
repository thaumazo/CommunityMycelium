from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.communities.models import Project
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Sets up project-specific roles and permissions"

    def handle(self, *args, **options):
        # Create project-specific groups
        projects_admin_group, _ = Group.objects.get_or_create(name="Projects Admin")
        projects_editor_group, _ = Group.objects.get_or_create(name="Projects Editor")
        projects_viewer_group, _ = Group.objects.get_or_create(name="Projects Viewer")

        # Get content type for Project model
        project_content_type = ContentType.objects.get_for_model(Project)

        # Get all permissions for Project model
        project_permissions = Permission.objects.filter(
            content_type=project_content_type
        )

        # Projects admin group gets all permissions for projects
        projects_admin_permissions = project_permissions.filter(
            codename__in=[
                "add_project",
                "change_project",
                "delete_project",
                "view_project",
                "delegate_project",
            ]
        )
        projects_admin_group.permissions.set(projects_admin_permissions)

        # Projects editor group gets view_project permission
        projects_editor_permissions = project_permissions.filter(
            codename__in=[
                "add_project",
                "view_project",
            ]
        )
        projects_editor_group.permissions.set(projects_editor_permissions)

        # Projects viewer group gets view_project permission
        projects_viewer_permissions = project_permissions.filter(
            codename__in=[
                "view_project",
            ]
        )
        projects_viewer_group.permissions.set(projects_viewer_permissions)

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully set up project-specific roles and permissions"
            )
        )
