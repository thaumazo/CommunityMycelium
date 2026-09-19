from django.db import migrations, models


def preserve_existing_ai_consent(apps, schema_editor):
    User = apps.get_model("users", "User")
    User.objects.filter(ai_transcript_processing=True).update(
        ai_processing_mode="third_party"
    )


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0020_user_onboarding_completed_sections"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="ai_pollination",
            field=models.BooleanField(
                default=False,
                help_text="Allow AI to find connections between this person's information and other people's moves, profiles, and regional metacrisis facets.",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="ai_processing_mode",
            field=models.CharField(
                choices=[
                    ("none", "No AI"),
                    ("local", "Local AI Processing"),
                    ("third_party", "Third Party AI (no training)"),
                ],
                default="none",
                help_text="Controls whether and where AI processing may occur.",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="website_theme",
            field=models.CharField(
                choices=[("light", "Light"), ("dark", "Dark")],
                default="light",
                max_length=8,
            ),
        ),
        migrations.RunPython(preserve_existing_ai_consent, migrations.RunPython.noop),
    ]