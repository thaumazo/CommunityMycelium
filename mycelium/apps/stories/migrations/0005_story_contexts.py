from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("stories", "0004_story_community_notes"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="story",
            name="event_end_at",
            field=models.DateTimeField(blank=True, help_text="Optional end time for this story (for ranges)", null=True),
        ),
        migrations.AddField(
            model_name="story",
            name="event_start_at",
            field=models.DateTimeField(blank=True, help_text="Optional start time for this story", null=True),
        ),
        migrations.AddField(
            model_name="story",
            name="time_precision",
            field=models.CharField(
                choices=[
                    ("none", "No time specified"),
                    ("point", "Single point in time"),
                    ("range", "Time range"),
                ],
                default="none",
                help_text="Whether this story is anchored at a point in time or a range",
                max_length=20,
            ),
        ),
        migrations.CreateModel(
            name="StoryGeoPin",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("latitude", models.DecimalField(decimal_places=6, max_digits=9)),
                ("longitude", models.DecimalField(decimal_places=6, max_digits=9)),
                (
                    "radius_m",
                    models.FloatField(
                        blank=True,
                        help_text="Optional radius in meters for area-based pins",
                        null=True,
                    ),
                ),
                ("label", models.CharField(blank=True, max_length=255)),
                (
                    "role",
                    models.CharField(
                        blank=True,
                        help_text="Optional role like origin, impact, or meeting_site",
                        max_length=50,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "story",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="geo_pins",
                        to="stories.story",
                    ),
                ),
            ],
            options={
                "ordering": ["created_at"],
            },
        ),
        migrations.CreateModel(
            name="StoryLink",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "relation_type",
                    models.CharField(
                        choices=[
                            ("continuation", "Continuation"),
                            ("evidence", "Evidence"),
                            ("response", "Response"),
                            ("child_narrative", "Child narrative"),
                            ("synthesis", "Synthesis"),
                        ],
                        default="continuation",
                        max_length=30,
                    ),
                ),
                ("note", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_story_links",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "from_story",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="outbound_links",
                        to="stories.story",
                    ),
                ),
                (
                    "to_story",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="inbound_links",
                        to="stories.story",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "unique_together": {("from_story", "to_story", "relation_type")},
            },
        ),
    ]
