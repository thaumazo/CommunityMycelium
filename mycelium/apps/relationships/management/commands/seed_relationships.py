from django.core.management.base import BaseCommand
from ...models import Relationship

class Command(BaseCommand):
    help = "Seeds the database with initial relationship data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding relationships...")

        relationship_templates = [
            {
                "title": "Person of Interest",
                "description": "Someone who's noted but not currently engaged",
            },
            {
                "title": "Community Member",
                "description": "A member of the community",
            },
        ]

        for template in relationship_templates:
            try:
                Relationship.objects.create(
                    title=template["title"],
                    description=template["description"],
                )
                self.stdout.write(f"Created relationship: {template['title']}")
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error creating {template['title']}: {e}"))

        self.stdout.write(self.style.SUCCESS("Successfully seeded relationships"))
