from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from django.utils import timezone
from ...models import Task

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds the database with initial task data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding tasks...")

        # Get all users
        users = User.objects.all()

        # Sample task titles and descriptions
        task_templates = [
            {
                "title": "Review Documentation",
                "description": "Review and update project documentation",
            },
            {
                "title": "Code Review",
                "description": "Review recent code changes and provide feedback",
            },
            {
                "title": "Bug Fix",
                "description": "Fix reported bugs in the application",
            },
            {
                "title": "Feature Implementation",
                "description": "Implement new feature requirements",
            },
            {
                "title": "Testing",
                "description": "Write and execute test cases",
            },
            {
                "title": "Deployment",
                "description": "Prepare and execute deployment process",
            },
            {
                "title": "Client Meeting",
                "description": "Prepare for and attend client meeting",
            },
            {
                "title": "Team Sync",
                "description": "Update team on progress and blockers",
            },
            {
                "title": "Performance Optimization",
                "description": "Optimize application performance",
            },
            {
                "title": "Security Audit",
                "description": "Conduct security audit and fix vulnerabilities",
            },
        ]

        # Create tasks for each user
        for user in users:
            # Create 3-5 tasks for each user
            num_tasks = 3  # Base number of tasks
            if user.username in ["whitnelson", "willgarrison"]:
                num_tasks = 5  # More tasks for the main users

            for i in range(num_tasks):
                # Get a random task template
                template = task_templates[i % len(task_templates)]

                # Calculate due date with timezone awareness
                due_date = timezone.now() + timedelta(days=i * 2)  # Every other day

                # Randomly assign status
                status = "pending"
                if i % 3 == 0:
                    status = "completed"
                elif i % 3 == 1:
                    status = "in_progress"

                Task.objects.create(
                    title=f"{template['title']} - {user.username}",
                    description=template["description"],
                    due_date=due_date,
                    status=status,
                    created_by=user,
                )

        self.stdout.write(self.style.SUCCESS("Successfully seeded tasks"))
