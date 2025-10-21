from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.communities.models import Relationship
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Sets up relationship-specific roles and permissions"

    def handle(self, *args, **options):
        # Create relationship-specific groups
        relationships_admin_group, _ = Group.objects.get_or_create(name="Relationships Admin")
        relationships_editor_group, _ = Group.objects.get_or_create(name="Relationships Editor")
        relationships_viewer_group, _ = Group.objects.get_or_create(name="Relationships Viewer")

        # Get content type for Relationship model
        relationship_content_type = ContentType.objects.get_for_model(Relationship)

        # Get all permissions for Relationship model
        relationship_permissions = Permission.objects.filter(
            content_type=relationship_content_type
        )

        # Relationships admin group gets all permissions for relationships
        relationships_admin_permissions = relationship_permissions.filter(
            codename__in=[
                "add_relationship",
                "change_relationship",
                "delete_relationship",
                "view_relationship",
                "delegate_relationship",
            ]
        )
        relationships_admin_group.permissions.set(relationships_admin_permissions)

        # Relationships editor group gets view_relationship permission
        relationships_editor_permissions = relationship_permissions.filter(
            codename__in=[
                "add_relationship",
                "view_relationship",
            ]
        )
        relationships_editor_group.permissions.set(relationships_editor_permissions)

        # Relationships viewer group gets view_relationship permission
        relationships_viewer_permissions = relationship_permissions.filter(
            codename__in=[
                "view_relationship",
            ]
        )
        relationships_viewer_group.permissions.set(relationships_viewer_permissions)

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully set up relationship-specific roles and permissions"
            )
        )
