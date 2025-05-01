from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from django.utils import timezone
import random
from ...models import Meeting

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds the database with initial meeting data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding meetings...")

        # Get all users
        users = User.objects.all()

        # Sample meeting titles and descriptions
        meeting_templates = [
            {
                "title": "Weekly Team Sync",
                "description": "Regular team meeting to discuss progress and blockers",
            },
            {
                "title": "Project Planning",
                "description": "Planning session for upcoming project milestones",
            },
            {
                "title": "Client Review",
                "description": "Review of client deliverables and feedback",
            },
            {
                "title": "Sprint Retrospective",
                "description": "Review of the last sprint and planning improvements",
            },
            {
                "title": "Product Demo",
                "description": "Demonstration of new features and functionality",
            },
            {
                "title": "Strategy Session",
                "description": "Long-term planning and strategy discussion",
            },
            {
                "title": "Code Review",
                "description": "Review of recent code changes and improvements",
            },
            {
                "title": "One-on-One",
                "description": "Individual check-in and progress review",
            },
            {
                "title": "Workshop",
                "description": "Hands-on session for learning new skills",
            },
            {
                "title": "Brainstorming",
                "description": "Creative session for generating new ideas",
            },
        ]

        # Create meetings for each user
        for user in users:
            # Create 3-5 meetings for each user
            num_meetings = random.randint(3, 5)  # Random number of meetings between 3 and 5
            if user.username in ["whitnelson", "willgarrison"]:
                num_meetings = random.randint(5, 8)  # More meetings for the main users

            for i in range(num_meetings):
                # Get a random meeting template
                template = random.choice(meeting_templates)

                # Generate random date within the next 30 days
                days_ahead = random.randint(0, 30)
                # Generate random time between 9 AM and 5 PM
                hour = random.randint(9, 16)
                minute = random.choice([0, 15, 30, 45])
                
                # Calculate start time
                start_time = timezone.now() + timedelta(days=days_ahead, hours=hour, minutes=minute)
                # Random duration between 30 minutes and 2 hours
                duration = random.randint(30, 120)
                end_time = start_time + timedelta(minutes=duration)

                Meeting.objects.create(
                    title=f"{template['title']}",
                    description=template["description"],
                    start_time=start_time,
                    end_time=end_time,
                    created_by=user,
                )

        self.stdout.write(self.style.SUCCESS("Successfully seeded meetings"))
