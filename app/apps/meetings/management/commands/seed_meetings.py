from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from django.utils import timezone
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
            num_meetings = 3  # Base number of meetings
            if user.username in ["whitnelson", "willgarrison"]:
                num_meetings = 5  # More meetings for the main users

            for i in range(num_meetings):
                # Get a random meeting template
                template = meeting_templates[i % len(meeting_templates)]

                # Calculate start and end times with timezone awareness
                start_time = timezone.now() + timedelta(
                    days=i * 2, hours=9
                )  # Every other day at 9 AM
                end_time = start_time + timedelta(hours=1)  # 1 hour duration

                Meeting.objects.create(
                    title=f"{template['title']} - {user.username}",
                    description=template["description"],
                    start_time=start_time,
                    end_time=end_time,
                    created_by=user,
                )

        self.stdout.write(self.style.SUCCESS("Successfully seeded meetings"))
