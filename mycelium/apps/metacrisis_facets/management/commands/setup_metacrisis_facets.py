from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.communities.models import Metacrisis_facet
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Sets up metacrisis facet-specific roles and permissions"

    def handle(self, *args, **options):
        # Create metacrisis_facet-specific groups
        metacrisis_facets_admin_group, _ = Group.objects.get_or_create(name="Metacrisis Facet Admin")
        metacrisis_facets_editor_group, _ = Group.objects.get_or_create(name="Metacrisis Facet Editor")
        metacrisis_facets_viewer_group, _ = Group.objects.get_or_create(name="Metacrisis Facet Viewer")

        # Get content type for Metacrisis Facet model
        metacrisis_facet_content_type = ContentType.objects.get_for_model(Metacrisis_facet)

        # Get all permissions for Metacrisis Facet model
        metacrisis_facet_permissions = Permission.objects.filter(
            content_type=metacrisis_facet_content_type
        )

        # Metacrisis Facet admin group gets all permissions for metacrisis facets
        metacrisis_facets_admin_permissions = metacrisis_facet_permissions.filter(
            codename__in=[
                "add_metacrisis_facet",
                "change_metacrisis_facet",
                "delete_metacrisis_facet",
                "view_metacrisis_facet",
                "delegate_metacrisis_facet",
            ]
        )
        metacrisis_facets_admin_group.permissions.set(metacrisis_facets_admin_permissions)

        # Metacrisis Facets editor group gets view_metacrisis_facet permission
        metacrisis_facets_editor_permissions = metacrisis_facet_permissions.filter(
            codename__in=[
                "add_metacrisis_facet",
                "view_metacrisis_facet",
            ]
        )
        metacrisis_facets_editor_group.permissions.set(metacrisis_facets_editor_permissions)

        # Metacrisis Facets viewer group gets view_metacrisis_facet permission
        metacrisis_facets_viewer_permissions = metacrisis_facet_permissions.filter(
            codename__in=[
                "view_metacrisis_facet",
            ]
        )
        metacrisis_facets_viewer_group.permissions.set(metacrisis_facets_viewer_permissions)

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully set up metacrisis_facet-specific roles and permissions"
            )
        )
