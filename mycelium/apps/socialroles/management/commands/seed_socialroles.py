from django.core.management.base import BaseCommand
from ...models import Socialrole


class Command(BaseCommand):
    help = "Seeds the database with initial social role data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding social roles...")

        socialrole_templates = [
            {"title": "Initiator", "description": "You start things. You act when others are still thinking. You’re good at sensing what needs to happen and taking the first step—even when the path isn’t clear yet. You often rally people before there’s a plan.", "image_path": "img/roles/Initiator.png"},
            {"title": "Synthesizer", "description": "You connect dots others don’t see. You hold multiple perspectives and help make things coherent. When people talk past each other, you find the throughline. When there’s chaos, you find structure.", "image_path": "img/roles/Synthesizer.png"},
            {"title": "Implementer", "description": "You turn ideas into action. You build, fix, move, execute. You like clear roles, working parts, and visible progress. You’re happiest when a project goes from plan to reality—and you were part of making it happen.", "image_path": "img/roles/Implementer.png"},
            {"title": "Sustainer", "description": "You’re the quiet backbone of teams and systems. You hold routines, check in, and keep people and projects from falling through the cracks. You think long-term and tend what others forget.", "image_path": "img/roles/Sustainer.png"},
            {"title": "Strategic Challenger", "description": "You’re willing to question what others avoid. You notice blind spots, power dynamics, and flawed assumptions. You push for truth, clarity, and change—not because you want conflict, but because you care.", "image_path": "img/roles/Strategic_Challenger.png"},
            {"title": "Relational Weaver", "description": "You know who’s connected to whom—and who should be. You build trust, hold relationships, and keep the social fabric strong. You make space for care, inclusion, and collaboration.", "image_path": "img/roles/Relational_Weaver.png"},
            {"title": "Pattern Tracker", "description": "You zoom out. You notice patterns over time, across systems, or under the surface. You help others see root causes, not just symptoms—and you often warn of risks before they arrive.", "image_path": "img/roles/Pattern_Tracker.png"},
            {"title": "Meaning Maker", "description": "You create clarity, resonance, and shared purpose. You use story, ritual, metaphor, or reflection to help people connect. You bring the “why” into the “what.” Without you, things feel flat or transactional.", "image_path": "img/roles/Meaning_Maker.png"},
            {"title": "Resource Mobilizer", "description": "You know how to find what’s needed—funds, tools, talent, space. You move resources where they’ll have the most impact. You’re pragmatic, creative, and often the person who knows a person.", "image_path": "img/roles/Resource_Mobilizer.png"},
            {"title": "Edgewalker", "description": "You explore new ways of thinking, creating, and organizing. You often live between worlds—bridging cultures, disciplines, or paradigms. You stretch what’s possible and bring back insights others might miss.", "image_path": "img/roles/Edgewalker.png"},
            {"title": "Experimenter", "description": "You prototype, iterate, and learn in motion. You thrive in uncertainty and enjoy learning by doing. You help groups evolve quickly and avoid perfection paralysis.", "image_path": "img/roles/Experimenter.png"},
            {"title": "Conflict Alchemist", "description": "You don’t just mediate—you transform. You help groups face hard things, shift stuck patterns, and emerge stronger. You move toward conflict, not away from it.", "image_path": "img/roles/Conflict_Alchemist.png"},
            {"title": "Sensemaker / Educator", "description": "You distill complexity. You turn big ideas into understandable guidance. You train, teach, or translate.", "image_path": "img/roles/Sensemaker.png"},
            {"title": "Caregiver / Nourisher", "description": "You tend people and the unseen. You notice what needs warmth, rest, or support, and you bring it. You create safety for others to grow, act, or speak.", "image_path": "img/roles/Caregiver.png"},
            {"title": "Guardian / Steward / Protector", "description": "You watch the edges. You hold ethical boundaries, protect the vulnerable, and help groups stay aligned with values, place, and purpose.", "image_path": "img/roles/Guardian.png"},
            {"title": "Welcomer", "description": "You notice who isn’t here yet—and you reach out. You welcome people into the space, meet them where they are, and help them find their place in the work. You make complexity feel less intimidating and community feel more human.", "image_path": "img/roles/Welcomer.png"},
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
