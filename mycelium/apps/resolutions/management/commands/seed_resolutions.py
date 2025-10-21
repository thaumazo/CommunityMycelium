from django.core.management.base import BaseCommand
from ...models import Resolution

class Command(BaseCommand):
    help = "Seeds the database with initial resolution data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding resolutions...")

        resolution_templates = [
            {
                "title": "Community Member Resolution",
                "description": "Resolution for Community Members",
            },
            {
                "title": "Team Lead",
                "description": "Resolution for Team Lead",
            },
        ]

        for template in resolution_templates:
            try:
                Resolution.objects.create(
                    title=template["title"],
                    description=template["description"],
                )
                self.stdout.write(f"Created resolution: {template['title']}")
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error creating {template['title']}: {e}"))

        self.stdout.write(self.style.SUCCESS("Successfully seeded resolutions"))
