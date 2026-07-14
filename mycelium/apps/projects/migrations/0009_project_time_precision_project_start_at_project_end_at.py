from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0008_project_locations_primary_location"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="time_precision",
            field=models.CharField(
                choices=[
                    ("none", "No time specified"),
                    ("point", "Single point in time"),
                    ("range", "Time range"),
                ],
                default="none",
                help_text="Whether this project is anchored at a point in time or a range.",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="project_start_at",
            field=models.DateTimeField(
                blank=True,
                help_text="Optional start time for this project",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="project_end_at",
            field=models.DateTimeField(
                blank=True,
                help_text="Optional end time for this project (for ranges)",
                null=True,
            ),
        ),
    ]
