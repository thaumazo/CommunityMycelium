from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from django.utils import timezone
from ...models import Socialrole

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds the database with initial social role data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding social roles...")

        # Get all users
        users = User.objects.all()

        # Sample social role titles and descriptions
        socialrole_templates = [
            {
                "title": "Test 1",
                "description": "This is a test",
            },
        ]

        self.stdout.write(self.style.SUCCESS("Successfully seeded social roles"))
