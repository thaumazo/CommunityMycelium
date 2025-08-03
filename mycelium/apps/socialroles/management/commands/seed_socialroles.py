from django.core.management.base import BaseCommand
from ...models import Socialrole


class Command(BaseCommand):
    help = "Seeds the database with initial social role data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding social roles...")

        socialrole_templates = [
            {"title": "Weavers", "description": "We see the through-lines of connectivity between people, places, organizations, ideas, and movements.", "image_path": "img/roles/01_Weavers.png"},
            {"title": "Experimenters", "description": "We innovate, pioneer, and invent. We take risks and course correct as needed.", "image_path": "img/roles/02_Experimenters.png"},
            {"title": "Frontline Responders", "description": "We address community crises by assembling and organizing resources, networks, and messages.", "image_path": "img/roles/03_FrontlineResponders.png"},
            {"title": "Visionaries", "description": "We imagine and generate our boldest possibilities, hopes, and dreams, and remind us of our direction.", "image_path": "img/roles/04_Visionaries.png"},
            {"title": "Builders", "description": "We develop, organize, and implement ideas, practices, people, and resources in service to a collective vision.", "image_path": "img/roles/05_Builders.png"},
            {"title": "Caregivers", "description": "We nurture and nourish the people around us by creating and sustaining a community of care, joy, and connection.", "image_path": "img/roles/06_Caregivers.png"},
            {"title": "Disruptors", "description": "We take uncomfortable and risky actions to shake up the status quo, to raise awareness, and to build power.", "image_path": "img/roles/07_Disrupters.png"},
            {"title": "Healers", "description": "We recognize and tend to the generational and current traumas caused by oppressive systems, institutions, policies, and practices.", "image_path": "img/roles/08_Healers.png"},
            {"title": "Storytellers", "description": "We craft and share our community stories, cultures, experiences, histories, and possibilities through word, art, music, media and movement.", "image_path": "img/roles/09_Storytellers.png"},
            {"title": "Guides", "description": "We teach, counsel, and advise, using our gifts of well-earned discernment and wisdom.", "image_path": "img/roles/10_Guides.png"},
        ]

        for template in socialrole_templates:
            obj, created = Socialrole.objects.get_or_create(
                title=template["title"],
                defaults={
                    "description": template["description"],
                    "image_path": template["image_path"]
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created: {obj.title}"))
            else:
                self.stdout.write(self.style.WARNING(f"Skipped (already exists): {obj.title}"))

        self.stdout.write(self.style.SUCCESS("✅ Done seeding social roles."))
