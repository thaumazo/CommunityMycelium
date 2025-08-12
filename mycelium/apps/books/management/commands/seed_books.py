from django.core.management.base import BaseCommand
from ...models import Book

class Command(BaseCommand):
    help = "Seeds the database with initial book data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding books...")

        book_templates = [
            {
                "title": "Book 1",
                "description": "Test Book",
            },
            {
                "title": "Book 2",
                "description": "Test Book",
            },
        ]

        for template in book_templates:
            try:
                Book.objects.create(
                    title=template["title"],
                    description=template["description"],
                )
                self.stdout.write(f"Created book: {template['title']}")
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error creating {template['title']}: {e}"))

        self.stdout.write(self.style.SUCCESS("Successfully seeded books"))
