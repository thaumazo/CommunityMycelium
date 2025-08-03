from django.core.management.base import BaseCommand
from ...models import Metacrisis_facet


class Command(BaseCommand):
    help = "Seeds the database with initial metacrisis facet data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding metacrisis facets...")

        metacrisis_facet_templates = [
            {"title": "Extinction Edge", "description": "These are threats that could lead to human extinction or permanently curtail humanity's potential. Examples include nuclear war, unchecked artificial intelligence, and catastrophic climate change. The existential risks are amplified by the interconnections between technology, environment, and global politics.", "image_path": "img/metacrisis_facets/1_ExtinctionEdge.png"},
            {"title": "Fragile Web", "description": "This facet involves the inherent vulnerabilities in our global systems—economic, political, environmental, and technological. As these systems become more interconnected, they also become more susceptible to cascading failures, where a disruption in one area can trigger a chain reaction of crises across multiple domains.", "image_path": "img/metacrisis_facets/2_FragileWeb.png"},
            {"title": "Truth Tornado", "description": "This refers to the breakdown of shared understanding and trust in knowledge systems. Misinformation, disinformation, the erosion of expertise, and the polarization of discourse contribute to this crisis, making it difficult for societies to agree on facts or to make collective decisions.", "image_path": "img/metacrisis_facets/3_TruthTornado.png"},
            {"title": "Soul Split", "description": "This facet involves the fragmentation of cultural narratives and identities, leading to a loss of meaning, purpose, and connection among individuals and communities. The increase in mental health issues, social isolation, and the decline of community bonds are in part symptomatic of this broader cultural and psychological unraveling.", "image_path": "img/metacrisis_facets/4_SoulSplit.png"},
            {"title": "Earth Erosion", "description": "The ecological aspect of the metacrisis includes environmental degradation, biodiversity loss, and climate change. These issues destabilize the natural systems upon which all life depends. The ecological crisis is exacerbated by human activities that disrupt the planet's ecosystems at a global scale.", "image_path": "img/metacrisis_facets/5_EarthErosion.png"},
            {"title": "Power Pyramid", "description": "Growing inequality, both within and between countries, is another critical element of the metacrisis. The concentration of wealth and power in the hands of a few, coupled with the disenfranchisement of large populations, fuels social unrest, destabilizes political systems, and hinders collective action to address global challenges.", "image_path": "img/metacrisis_facets/6_PowerPyramid.png"},
            {"title": "Tech Tsunami", "description": "Advances in technology, particularly in artificial intelligence, biotechnology, and digital surveillance, pose both opportunities and risks. The rapid pace of technological change outstrips the capacity of social, legal, and ethical systems to keep up, leading to unintended consequences and new forms of control and exploitation.", "image_path": "img/metacrisis_facets/7_TechTsunami.png"},
            {"title": "Leadership Lapse", "description": "Many of the world's governance systems are not equipped to handle the complexity of the metacrisis. These systems often operate in silos, are slow to adapt, and are prone to corruption, inefficiency, and short-term thinking. This governance deficit makes it difficult to coordinate global responses to interconnected crises.", "image_path": "img/metacrisis_facets/8_LeadershipLapse.png"},
        ]
        for template in metacrisis_facet_templates:
            obj, created = Metacrisis_facet.objects.get_or_create(
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

        self.stdout.write(self.style.SUCCESS("✅ Done seeding metacrisis facets."))
