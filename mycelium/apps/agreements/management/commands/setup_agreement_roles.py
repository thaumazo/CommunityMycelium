from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.communities.models import Agreement
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Sets up agreement-specific roles and permissions"

    def handle(self, *args, **options):
        # Create agreement-specific groups
        agreement_admin_group, _ = Group.objects.get_or_create(name="Agreements Admin")
        agreement_editor_group, _ = Group.objects.get_or_create(name="Agreements Editor")
        agreement_viewer_group, _ = Group.objects.get_or_create(name="Agreements Viewer")

        # Get content type for Agreement model
        agreement_content_type = ContentType.objects.get_for_model(Agreement)

        # Get all permissions for Agreement model
        agreement_permissions = Permission.objects.filter(
            content_type=agreement_content_type
        )

        # Agreements admin group gets all permissions for agreements
        agreements_admin_permissions = agreement_permissions.filter(
            codename__in=[
                "add_agreement",
                "change_agreement",
                "delete_agreement",
                "view_agreement",
                "delegate_agreement",
            ]
        )
        agreements_admin_group.permissions.set(agreements_admin_permissions)

        # Agreements editor group gets view_agreement permission
        agreements_editor_permissions = agreement_permissions.filter(
            codename__in=[
                "add_agreement",
                "view_agreement",
            ]
        )
        agreements_editor_group.permissions.set(agreements_editor_permissions)

        # Agreements viewer group gets view_agreement permission
        agreements_viewer_permissions = agreement_permissions.filter(
            codename__in=[
                "view_agreement",
            ]
        )
        agreements_viewer_group.permissions.set(agreements_viewer_permissions)

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully set up agreement-specific roles and permissions"
            )
        )
