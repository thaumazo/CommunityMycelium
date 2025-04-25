from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds the database with initial user data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding users...")

        # Create first user
        User.objects.create_user(
            username="whitnelson", email="whitnelson@gmail.com", password="Asdfdsa1.."
        )

        # Create second user
        User.objects.create_user(
            username="willgarrison",
            email="willgarrison@gmail.com",
            password="Asdfdsa1..",
        )

        # Additional random users
        dummy_users = [
            {"username": "alexsmith", "email": "alex.smith@example.com"},
            {"username": "jennifer_lee", "email": "jennifer.lee@example.com"},
            {"username": "michaelbrown", "email": "michael.brown@example.com"},
            {"username": "sarah_wilson", "email": "sarah.wilson@example.com"},
            {"username": "davidmiller", "email": "david.miller@example.com"},
            {"username": "emily_jones", "email": "emily.jones@example.com"},
            {"username": "robertwhite", "email": "robert.white@example.com"},
            {"username": "laura_davis", "email": "laura.davis@example.com"},
            {"username": "thomastaylor", "email": "thomas.taylor@example.com"},
            {"username": "olivia_moore", "email": "olivia.moore@example.com"},
        ]

        # Create additional users with the same password
        for user_data in dummy_users:
            User.objects.create_user(
                username=user_data["username"],
                email=user_data["email"],
                password="Asdfdsa1..",
            )

        self.stdout.write(self.style.SUCCESS("Successfully seeded users"))
