from django.core.management.base import BaseCommand
from ...models import Capital


class Command(BaseCommand):
    help = "Seeds the database with initial capital data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding capital schemas...")

        capital_templates = [
            {"title": "Financial", "description": "Money, currencies, credit, investments, and tokens of exchange value.", "image_path": "img/capitals/01_financial.png"},
            {"title": "Material", "description": "The tangible, human-made or harvested objects: buildings, tools, vehicles, infrastructure, renewable tech, local goods, fiber, fuel.", "image_path": "img/capitals/02_material.png"},
            {"title": "Natural", "description": "The living and non-living systems of the bioregion—forests, rivers, soil, air, minerals, biodiversity, climate, fungi, wetlands.", "image_path": "img/capitals/03_natural.png"},
            {"title": "Social", "description": "Relationships, trust, networks, cooperation, shared norms, and mutual aid.", "image_path": "img/capitals/04_social.png"},
            {"title": "Intellectual", "description": "Knowledge, systems thinking, know-how, design methods, data, patterns, and models.", "image_path": "img/capitals/05_intellectual.png"},
            {"title": "Experiential", "description": "Embodied practice, lessons learned, skillsets earned through time and doing—often tacit or locally specific.", "image_path": "img/capitals/06_experiential.png"},
            {"title": "Cultural", "description": "Art, language, shared symbols, heritage, traditions, rituals, values, and aesthetic ways of being.", "image_path": "img/capitals/07_cultural.png"},
            {"title": "Spiritual", "description": "Meaning-making, connection to the sacred, inner transformation, purpose, awe, and alignment with something greater.", "image_path": "img/capitals/08_spiritual.png"},
        ]
        for template in capital_templates:
            obj, created = Capital.objects.get_or_create(
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

        self.stdout.write(self.style.SUCCESS("✅ Done seeding capitals."))
