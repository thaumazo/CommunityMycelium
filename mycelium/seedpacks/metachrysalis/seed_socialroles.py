from django.core.management.base import BaseCommand
from ...models import Socialrole


class Command(BaseCommand):
    help = "Seeds the database with initial social role data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding social roles...")

        socialrole_templates = [
            {"title": "Weavers", "description": "We see the through-lines of connectivity between people, places, organizations, ideas, and movements."},
            {"title": "Experimenters", "description": "We innovate, pioneer, and invent. We take risks and course correct as needed."},
            {"title": "Frontline Responders", "description": "We address community crises by assembling and organizing resources, networks, and messages."},
            {"title": "Visionaries", "description": "We imagine and generate our boldest possibilities, hopes, and dreams, and remind us of our direction."},
            {"title": "Builders", "description": "We develop, organize, and implement ideas, practices, people, and resources in service to a collective vision."},
            {"title": "Caregivers", "description": "We nurture and nourish the people around us by creating and sustaining a community of care, joy, and connection."},
            {"title": "Disruptors", "description": "We take uncomfortable and risky actions to shake up the status quo, to raise awareness, and to build power."},
            {"title": "Healers", "description": "We recognize and tend to the generational and current traumas caused by oppressive systems, institutions, policies, and practices."},
            {"title": "Storytellers", "description": "We craft and share our community stories, cultures, experiences, histories, and possibilities through word, art, music, media and movement."},
            {"title": "Guides", "description": "We teach, counsel, and advise, using our gifts of well-earned discernment and wisdom."},
        ]

        for template in socialrole_templates:
            obj, created = Socialrole.objects.get_or_create(
                title=template["title"],
                defaults={"description": template["description"]}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created: {obj.title}"))
            else:
                self.stdout.write(self.style.WARNING(f"Skipped (already exists): {obj.title}"))

        self.stdout.write(self.style.SUCCESS("✅ Done seeding social roles."))
