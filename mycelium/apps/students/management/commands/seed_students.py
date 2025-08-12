from django.core.management.base import BaseCommand
from ...models import Student

class Command(BaseCommand):
    help = "Seeds the database with initial student data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding students...")

        student_templates = [
            {
                "title": "Student 1",
                "description": "Test Student",
            },
            {
                "title": "Student 2",
                "description": "Test Student",
            },
        ]

        for template in student_templates:
            try:
                Student.objects.create(
                    title=template["title"],
                    description=template["description"],
                )
                self.stdout.write(f"Created student: {template['title']}")
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error creating {template['title']}: {e}"))

        self.stdout.write(self.style.SUCCESS("Successfully seeded students"))
