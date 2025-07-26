from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.communities.models import Bioregion
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Sets up bioregion-specific roles and permissions"

    def handle(self, *args, **options):
        # Create bioregion-specific groups
        bioregions_admin_group, _ = Group.objects.get_or_create(name="Bioregions Admin")
        bioregions_editor_group, _ = Group.objects.get_or_create(name="Bioregions Editor")
        bioregions_viewer_group, _ = Group.objects.get_or_create(name="Bioregions Viewer")

        # Get content type for Bioregion model
        bioregion_content_type = ContentType.objects.get_for_model(Bioregion)

        # Get all permissions for Bioregion model
        bioregion_permissions = Permission.objects.filter(
            content_type=bioregion_content_type
        )

        # Bioregions admin group gets all permissions for bioregions
        bioregions_admin_permissions = bioregion_permissions.filter(
            codename__in=[
                "add_bioregion",
                "change_bioregion",
                "delete_bioregion",
                "view_bioregion",
                "delegate_bioregion",
            ]
        )
        bioregions_admin_group.permissions.set(bioregions_admin_permissions)

        # Bioregions editor group gets view_bioregion permission
        bioregions_editor_permissions = bioregion_permissions.filter(
            codename__in=[
                "add_bioregion",
                "view_bioregion",
            ]
        )
        bioregions_editor_group.permissions.set(bioregions_editor_permissions)

        # Bioregions viewer group gets view_bioregion permission
        bioregions_viewer_permissions = bioregion_permissions.filter(
            codename__in=[
                "view_bioregion",
            ]
        )
        bioregions_viewer_group.permissions.set(bioregions_viewer_permissions)

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully set up bioregion-specific roles and permissions"
            )
        )
