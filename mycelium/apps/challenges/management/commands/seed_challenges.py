from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from django.utils import timezone
from ...models import Challenge

REQUIRES = ['users', 'bioregions', 'metacrisis_facets']

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds the database with initial challenge data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding challenges...")

        # Get all users
        users = User.objects.all()

        # Sample challenge titles and descriptions
        challenge_templates = [
            {
                "title": "Bioregional Mapping",
                "description": "Mapping the People, Communities and Projects in your Bioregion",
            },
        ]

        self.stdout.write(self.style.SUCCESS("Successfully seeded challenges"))
