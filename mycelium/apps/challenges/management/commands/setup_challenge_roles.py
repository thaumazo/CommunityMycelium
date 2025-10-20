from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.communities.models import Challenge
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Sets up challenge-specific roles and permissions"

    def handle(self, *args, **options):
        # Create challenge-specific groups
        challenges_admin_group, _ = Group.objects.get_or_create(name="Challenges Admin")
        challenges_editor_group, _ = Group.objects.get_or_create(name="Challenges Editor")
        challenges_viewer_group, _ = Group.objects.get_or_create(name="Challenges Viewer")

        # Get content type for Challenge model
        challenge_content_type = ContentType.objects.get_for_model(Challenge)

        # Get all permissions for Challenge model
        challenge_permissions = Permission.objects.filter(
            content_type=challenge_content_type
        )

        # Challenges admin group gets all permissions for challenges
        challenges_admin_permissions = challenge_permissions.filter(
            codename__in=[
                "add_challenge",
                "change_challenge",
                "delete_challenge",
                "view_challenge",
                "delegate_challenge",
            ]
        )
        challenges_admin_group.permissions.set(challenges_admin_permissions)

        # Challenges editor group gets view_challenge permission
        challenges_editor_permissions = challenge_permissions.filter(
            codename__in=[
                "add_challenge",
                "view_challenge",
            ]
        )
        challenges_editor_group.permissions.set(challenges_editor_permissions)

        # Challenges viewer group gets view_challenge permission
        challenges_viewer_permissions = challenge_permissions.filter(
            codename__in=[
                "view_challenge",
            ]
        )
        challenges_viewer_group.permissions.set(challenges_viewer_permissions)

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully set up challenge-specific roles and permissions"
            )
        )
