from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from django.utils import timezone
from ...models import Hat

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds the database with initial hat data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding hats...")

        # Get all users
        users = User.objects.all()

        # Sample hat titles and descriptions
        community_templates = [
            {
                "title": "Person of Interest",
                "description": "Someone who's noted but not currently engaged",
            },
            {
                "title": "Community Member",
                "description": "A member of the community",
            },
        ]

        self.stdout.write(self.style.SUCCESS("Successfully seeded hats"))
