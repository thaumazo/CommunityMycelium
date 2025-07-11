from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.communities.models import Community
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Sets up community-specific roles and permissions"

    def handle(self, *args, **options):
        # Create community-specific groups
        communities_admin_group, _ = Group.objects.get_or_create(name="Communities Admin")
        communities_editor_group, _ = Group.objects.get_or_create(name="Communities Editor")
        communities_viewer_group, _ = Group.objects.get_or_create(name="Communities Viewer")

        # Get content type for Community model
        community_content_type = ContentType.objects.get_for_model(Community)

        # Get all permissions for Community model
        community_permissions = Permission.objects.filter(
            content_type=community_content_type
        )

        # Communities admin group gets all permissions for communities
        communities_admin_permissions = community_permissions.filter(
            codename__in=[
                "add_community",
                "change_community",
                "delete_community",
                "view_community",
                "delegate_community",
            ]
        )
        communities_admin_group.permissions.set(communities_admin_permissions)

        # Communities editor group gets view_community permission
        communities_editor_permissions = community_permissions.filter(
            codename__in=[
                "add_community",
                "view_community",
            ]
        )
        communities_editor_group.permissions.set(communities_editor_permissions)

        # Communities viewer group gets view_community permission
        communities_viewer_permissions = community_permissions.filter(
            codename__in=[
                "view_community",
            ]
        )
        communities_viewer_group.permissions.set(communities_viewer_permissions)

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully set up community-specific roles and permissions"
            )
        )
