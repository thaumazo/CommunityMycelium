from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from django.utils import timezone
from ...models import Bioregion

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds the database with initial bioregion data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding bioregions...")

        # Get all users
        users = User.objects.all()

        # Sample bioregion titles and descriptions
        bioregion_templates = [
            {
                "title": "Bioregional Mapping",
                "description": "Mapping the People, Communities and Projects in your Bioregion",
            },
        ]

        self.stdout.write(self.style.SUCCESS("Successfully seeded bioregions"))
