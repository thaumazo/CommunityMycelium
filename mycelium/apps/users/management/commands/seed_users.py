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
      
        # Output success message
        self.stdout.write(self.style.SUCCESS("Successfully seeded users"))
