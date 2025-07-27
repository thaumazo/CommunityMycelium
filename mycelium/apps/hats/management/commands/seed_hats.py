from django.core.management.base import BaseCommand
from ...models import Hat

class Command(BaseCommand):
    help = "Seeds the database with initial hat data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding hats...")

        hat_templates = [
            {
                "title": "Person of Interest",
                "description": "Someone who's noted but not currently engaged",
            },
            {
                "title": "Community Member",
                "description": "A member of the community",
            },
        ]

        for template in hat_templates:
            try:
                Hat.objects.create(
                    title=template["title"],
                    description=template["description"],
                )
                self.stdout.write(f"Created hat: {template['title']}")
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error creating {template['title']}: {e}"))

        self.stdout.write(self.style.SUCCESS("Successfully seeded hats"))
