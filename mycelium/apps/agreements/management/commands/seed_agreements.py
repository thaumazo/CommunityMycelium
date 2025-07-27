from django.core.management.base import BaseCommand
from ...models import Agreement

class Command(BaseCommand):
    help = "Seeds the database with initial agreement data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding agreements...")

        agreement_templates = [
            {
                "title": "Community Member Agreement",
                "description": "Agreement for Community Members",
            },
            {
                "title": "Team Lead",
                "description": "Agreement for Team Lead",
            },
        ]

        for template in agreement_templates:
            try:
                Agreement.objects.create(
                    title=template["title"],
                    description=template["description"],
                )
                self.stdout.write(f"Created agreement: {template['title']}")
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error creating {template['title']}: {e}"))

        self.stdout.write(self.style.SUCCESS("Successfully seeded agreements"))
