from django.core.management.base import BaseCommand
from ...models import Maladaptive


class Command(BaseCommand):
    help = "Seeds the database with initial maladaptive schema data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding maladaptive schemas...")

        maladaptive_templates = [
            {"title": "Emotional Deprivation", "description": "The belief and expectation that your primary needs will never be met. The sense that no one will nurture, care for, guide, protect or empathize with you.", "image_path": "img/maladaptives/01_emotional_deprivation.png"},
            {"title": "Abandonment", "description": "The belief and expectation that others will leave, that others are unreliable, that relationships are fragile, that loss is inevitable, and that you will ultimately wind up alone.", "image_path": "img/maladaptives/02_abandonment.png"},
            {"title": "Mistrust / Abuse", "description": "The belief that others are abusive, manipulative, selfish, or looking to hurt or use you. Others are not to be trusted.", "image_path": "img/maladaptives/03_mistrust.png"},
            {"title": "Defectiveness", "description": "The belief that you are flawed, damaged or unlovable, and you will thereby be rejected.", "image_path": "img/maladaptives/04_defectiveness.png"},
            {"title": "Social Isolation", "description": "The pervasive sense of aloneness, coupled with a feeling of alienation", "image_path": "img/maladaptives/05_social_isolation.png"},
            {"title": "Vulnerability", "description": "The sense that the world is a dangerous place, that disaster can happen at any time, and that you will be overwhelmed by the challenges that lie ahead.", "image_path": "img/maladaptives/06_vulnerability.png"},
            {"title": "Dependence / Incompetence", "description": "The belief that you are unable to effectively make your own decisions, that your judgment is questionable, and that you need to rely on others to help get you through day-to-day responsibilities.", "image_path": "img/maladaptives/07_dependence.png"},
            {"title": "Emotional Enmeshment / Undeveloped Self", "description": "The sense that you do not have an identity or “individuated self” that is separate from one or more significant others.", "image_path": "img/maladaptives/08_emotional_enmeshment.png"},
            {"title": "Failure", "description": "The expectation that you will fail, or belief that you cannot perform well enough.", "image_path": "img/maladaptives/09_failure.png"},
            {"title": "Subjugation", "description": "The belief that you must submit to the control of others, or else punishment or rejection will be forthcoming.", "image_path": "img/maladaptives/10_subjugation.png"},
            {"title": "Self-Sacrifice", "description": "The belief that you should voluntarily give up of your own needs for the sake of others, usually to a point which is excessive.", "image_path": "img/maladaptives/11_self_sacrifice.png"},
            {"title": "Approval-Seeking / Recognition-Seeking", "description": "The sense that approval, attention and recognition are far more important than genuine self-expression and being true to oneself.", "image_path": "img/maladaptives/12_approval_seeking.png"},
            {"title": "Emotional Inhibition", "description": "The belief that you must control your self-expression or others will reject or criticize you.", "image_path": "img/maladaptives/13_emotional_inhibition.png"},
            {"title": "Negativity / Pessimism", "description": "The pervasive belief that the negative aspects of life outweigh the positive, along with negative expectations for the future.", "image_path": "img/maladaptives/14_negativity.png"},
            {"title": "Unrelenting Standards", "description": "The belief that you need to be the best, always striving for perfection or to avoid mistakes.", "image_path": "img/maladaptives/15_unrelenting_standards.png"},
            {"title": "Punitiveness", "description": "The belief that people should be harshly punished for their mistakes or shortcomings.", "image_path": "img/maladaptives/16_punitiveness.png"},
            {"title": "Entitlement / Grandiosity", "description": "The sense that you are special or more important than others, and that you do not have to follow the rules like other people even though it may have a negative effect on others. Also can manifest in an exaggerated focus on superiority for the purpose of having power or control.", "image_path": "img/maladaptives/17_entitlement.png"},
            {"title": "Insufficient Self-Control / Self-Discipline", "description": "The sense that you cannot accomplish your goals, especially if the process contains boring, repetitive, or frustrating aspects. Also, that you cannot resist acting upon impulses that lead to detrimental results.", "image_path": "img/maladaptives/18_insufficient_self_control.png"},
        ]
        for template in maladaptive_templates:
            obj, created = Maladaptive.objects.get_or_create(
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

        self.stdout.write(self.style.SUCCESS("✅ Done seeding maladaptive schema."))
