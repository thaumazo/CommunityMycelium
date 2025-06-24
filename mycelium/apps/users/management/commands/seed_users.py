from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds the database with initial user data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding users...")

        # Create first user
        User.objects.create_user(
            username="whit",
            email="whitnelson@gmail.com",
            password="Asdfdsa1",
            full_name="Whit Nelson",
        )

        # Create second user
        User.objects.create_user(
            username="will",
            email="willgarrison@gmail.com",
            password="Asdfdsa1",
            full_name="Will Garrison",
        )

        # Additional random users
        dummy_users = [
            {
                "username": "alexsmith",
                "email": "alex.smith@example.com",
                "full_name": "Alex Smith",
            },
            {
                "username": "jennifer_lee",
                "email": "jennifer.lee@example.com",
                "full_name": "Jennifer Lee",
            },
            {
                "username": "michaelbrown",
                "email": "michael.brown@example.com",
                "full_name": "Michael Brown",
            },
            {
                "username": "sarah_wilson",
                "email": "sarah.wilson@example.com",
                "full_name": "Sarah Wilson",
            },
            {
                "username": "davidmiller",
                "email": "david.miller@example.com",
                "full_name": "David Miller",
            },
            {
                "username": "emily_jones",
                "email": "emily.jones@example.com",
                "full_name": "Emily Jones",
            },
            {
                "username": "robertwhite",
                "email": "robert.white@example.com",
                "full_name": "Robert White",
            },
            {
                "username": "laura_davis",
                "email": "laura.davis@example.com",
                "full_name": "Laura Davis",
            },
            {
                "username": "thomastaylor",
                "email": "thomas.taylor@example.com",
                "full_name": "Thomas Taylor",
            },
            {
                "username": "no_group_john",
                "email": "no_group_john@example.com",
                "full_name": "No Group John",
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

        # Add users to groups
        admin_group.user_set.add(User.objects.get(username="whit"))
        admin_group.user_set.add(User.objects.get(username="will"))

        # Add users to meetings groups
        meetings_admin_group = Group.objects.get(name="Meetings Admin")
        meetings_admin_group.user_set.add(User.objects.get(username="alexsmith"))
        meetings_admin_group.user_set.add(User.objects.get(username="jennifer_lee"))

        # Add users to meetings editor group
        meetings_editor_group = Group.objects.get(name="Meetings Editor")
        meetings_editor_group.user_set.add(User.objects.get(username="michaelbrown"))
        meetings_editor_group.user_set.add(User.objects.get(username="sarah_wilson"))

        # Add users to meetings viewer group
        meetings_viewer_group = Group.objects.get(name="Meetings Viewer")
        meetings_viewer_group.user_set.add(User.objects.get(username="davidmiller"))
        meetings_viewer_group.user_set.add(User.objects.get(username="emily_jones"))
        meetings_viewer_group.user_set.add(User.objects.get(username="robertwhite"))
        meetings_viewer_group.user_set.add(User.objects.get(username="laura_davis"))
        meetings_viewer_group.user_set.add(User.objects.get(username="thomastaylor"))

        # Add users to tasks admin group
        tasks_admin_group = Group.objects.get(name="Tasks Admin")
        tasks_admin_group.user_set.add(User.objects.get(username="alexsmith"))
        tasks_admin_group.user_set.add(User.objects.get(username="jennifer_lee"))

        # Add users to tasks editor group
        tasks_editor_group = Group.objects.get(name="Tasks Editor")
        tasks_editor_group.user_set.add(User.objects.get(username="michaelbrown"))
        tasks_editor_group.user_set.add(User.objects.get(username="sarah_wilson"))

        # Add users to tasks viewer group
        tasks_viewer_group = Group.objects.get(name="Tasks Viewer")
        tasks_viewer_group.user_set.add(User.objects.get(username="davidmiller"))
        tasks_viewer_group.user_set.add(User.objects.get(username="emily_jones"))
        tasks_viewer_group.user_set.add(User.objects.get(username="robertwhite"))
        tasks_viewer_group.user_set.add(User.objects.get(username="laura_davis"))
        tasks_viewer_group.user_set.add(User.objects.get(username="thomastaylor"))

        # Add users to user admin group
        user_admin_group = Group.objects.get(name="User Admin")
        user_admin_group.user_set.add(User.objects.get(username="alexsmith"))
        user_admin_group.user_set.add(User.objects.get(username="jennifer_lee"))

        # Add users to user viewer group
        user_viewer_group = Group.objects.get(name="User Viewer")
        user_viewer_group.user_set.add(User.objects.get(username="michaelbrown"))
        user_viewer_group.user_set.add(User.objects.get(username="sarah_wilson"))
        user_viewer_group.user_set.add(User.objects.get(username="davidmiller"))
        user_viewer_group.user_set.add(User.objects.get(username="emily_jones"))
        user_viewer_group.user_set.add(User.objects.get(username="robertwhite"))
        user_viewer_group.user_set.add(User.objects.get(username="laura_davis"))
        user_viewer_group.user_set.add(User.objects.get(username="thomastaylor"))

        # Output success message
        self.stdout.write(self.style.SUCCESS("Successfully seeded users"))
