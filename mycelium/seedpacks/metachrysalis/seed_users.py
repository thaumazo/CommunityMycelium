from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds the database with initial user data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding users...")

        # Additional random users
        dummy_users = [
            {
                "username": "daniel", "email": "daniel@daniellindenberger.com", "full_name": "Daniel Lindenberger",
            },
        ]

        # Create additional users with the same password
        for user_data in dummy_users:
            User.objects.create_user(
                username=user_data["username"],
                email=user_data["email"],
                password="Asdfdsa1..",
                full_name=user_data["full_name"],
            )

        # Get groups
        admin_group = Group.objects.get(name="Admin")

        # Add users to meetings groups
        meetings_admin_group = Group.objects.get(name="Meetings Admin")
        meetings_admin_group.user_set.add(User.objects.get(username="daniel"))

        # Add users to meetings editor group
        meetings_editor_group = Group.objects.get(name="Meetings Editor")
        meetings_editor_group.user_set.add(User.objects.get(username="daniel"))

        # Add users to meetings viewer group
        meetings_viewer_group = Group.objects.get(name="Meetings Viewer")
        meetings_viewer_group.user_set.add(User.objects.get(username="daniel"))

        # Add users to tasks admin group
        tasks_admin_group = Group.objects.get(name="Tasks Admin")
        tasks_admin_group.user_set.add(User.objects.get(username="daniel"))

        # Add users to tasks editor group
        tasks_editor_group = Group.objects.get(name="Tasks Editor")
        tasks_editor_group.user_set.add(User.objects.get(username="daniel"))

        # Add users to tasks viewer group
        tasks_viewer_group = Group.objects.get(name="Tasks Viewer")
        tasks_viewer_group.user_set.add(User.objects.get(username="daniel"))

        # Add users to user admin group
        user_admin_group = Group.objects.get(name="User Admin")
        user_admin_group.user_set.add(User.objects.get(username="fidanielzzgig"))

        # Add users to user viewer group
        user_viewer_group = Group.objects.get(name="User Viewer")
        user_viewer_group.user_set.add(User.objects.get(username="daniel"))

        # Output success message
        self.stdout.write(self.style.SUCCESS("Successfully seeded users"))
