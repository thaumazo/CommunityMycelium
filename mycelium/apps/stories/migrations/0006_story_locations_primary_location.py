from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("locations", "0002_location_bioregions"),
        ("stories", "0005_story_contexts"),
    ]

    operations = [
        migrations.AddField(
            model_name="story",
            name="locations",
            field=models.ManyToManyField(
                blank=True,
                help_text="Locations connected to this story.",
                related_name="stories",
                to="locations.location",
            ),
        ),
        migrations.AddField(
            model_name="story",
            name="primary_location",
            field=models.ForeignKey(
                blank=True,
                help_text="Primary map location for this story.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="primary_stories",
                to="locations.location",
            ),
        ),
    ]
