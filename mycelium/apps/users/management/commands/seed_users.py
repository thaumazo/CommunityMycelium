from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds the database with initial user data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding users...")

        # Create or update first user
        user, created = User.objects.get_or_create(
            username="whit",
            defaults={
                "email": "whitnelson@gmail.com",
                "full_name": "Whit Nelson",
                "is_email_verified": True,
                "is_active": True,
            }
        )
        user.set_password("Asdfdsa1")
        user.is_email_verified = True
        user.is_active = True
        user.save()

        # Create or update second user
        user, created = User.objects.get_or_create(
            username="will",
            defaults={
                "email": "willgarrison@gmail.com",
                "full_name": "Will Garrison",
                "is_email_verified": True,
                "is_active": True,
            }
        )
        user.set_password("Asdfdsa1")
        user.is_email_verified = True
        user.is_active = True
        user.save()

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

        # Create or update additional users
        for user_data in dummy_users:
            user, created = User.objects.get_or_create(
                username=user_data["username"],
                defaults={
                    "email": user_data["email"],
                    "full_name": user_data["full_name"],
                    "is_email_verified": True,
                    "is_active": True,
                }
            )
            user.set_password("Asdfdsa1..")
            user.is_email_verified = True
            user.is_active = True
            user.save()

        # Get groups
        admin_group = Group.objects.get(name="Admin")
        editor_group = Group.objects.get(name="Editor")
        viewer_group = Group.objects.get(name="Viewer")

        # Add users to groups
        admin_group.user_set.add(User.objects.get(username="whit"))
        admin_group.user_set.add(User.objects.get(username="will"))
        editor_group.user_set.add(User.objects.get(username="alexsmith"))
        editor_group.user_set.add(User.objects.get(username="jennifer_lee"))
        editor_group.user_set.add(User.objects.get(username="michaelbrown"))
        editor_group.user_set.add(User.objects.get(username="sarah_wilson"))
        viewer_group.user_set.add(User.objects.get(username="davidmiller"))
        viewer_group.user_set.add(User.objects.get(username="emily_jones"))
        viewer_group.user_set.add(User.objects.get(username="robertwhite"))
        viewer_group.user_set.add(User.objects.get(username="laura_davis"))
        viewer_group.user_set.add(User.objects.get(username="thomastaylor"))

        # Output success message
        self.stdout.write(self.style.SUCCESS("Successfully seeded users"))
