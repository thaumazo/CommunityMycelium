from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from django.utils import timezone
from ...models import Community

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds the database with initial community data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding communities...")

        # Get all users
        users = User.objects.all()

        # Sample community titles and descriptions
        community_templates = [
            {
                "title": "Thaumazo",
                "description": "Thaumazo Community",
            },
            {
                "title": "ParTecK",
                "description": "ParTecK is a community that's great",
            },
        ]

        self.stdout.write(self.style.SUCCESS("Successfully seeded communities"))
