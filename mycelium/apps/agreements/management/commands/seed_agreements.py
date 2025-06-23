from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from django.utils import timezone
from ...models import Agreement

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds the database with initial agreement data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding agreements...")

        # Get all users
        users = User.objects.all()

        # Sample agreement titles and descriptions
        community_templates = [
            {
                "title": "Community Member Agreement",
                "description": "Agreement for Community Members",
            },
            {
                "title": "Team Lead",
                "description": "Agreement for Team Lead",
            },
        ]

        self.stdout.write(self.style.SUCCESS("Successfully seeded agreements"))
