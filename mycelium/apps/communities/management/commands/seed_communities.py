from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from ...models import Community

User = get_user_model()

class Command(BaseCommand):
    help = "Seeds the database with initial community data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding communities...")

        # Sample community titles and descriptions
        community_templates = [
            {"title": "Thaumazo", "description": "Thaumazo Nonprofit Community"},
            {"title": "ParTecK", "description": "ParTecK"},
        ]

        for template in community_templates:
            try:
                Community.objects.create(
                    title=template["title"],
                    description=template["description"],
                )
                self.stdout.write(f"Created community: {template['title']}")
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error creating {template['title']}: {e}"))

        self.stdout.write(self.style.SUCCESS("Successfully seeded communities"))
