from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("stories", "0003_story_youtube_url"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="story",
            name="community_note_decided_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="story",
            name="community_note_decided_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="decided_community_notes",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="story",
            name="community_note_status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("promoted", "Promoted"),
                    ("declined", "Declined"),
                ],
                default="pending",
                help_text="Decision status for community note review.",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="story",
            name="community_note_type",
            field=models.CharField(
                choices=[("none", "None"), ("idea", "Idea"), ("offer", "Offer")],
                default="none",
                help_text="Type of community note (idea or offer).",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="story",
            name="is_community_note",
            field=models.BooleanField(
                default=False,
                help_text="Whether this story was submitted as a project community note.",
            ),
        ),
    ]
