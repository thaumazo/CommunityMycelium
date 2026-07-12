from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("locations", "0002_location_bioregions"),
        ("projects", "0007_project_phase_state_unknown_defaults"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="locations",
            field=models.ManyToManyField(
                blank=True,
                help_text="Locations this project is connected to",
                related_name="projects",
                to="locations.location",
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="primary_location",
            field=models.ForeignKey(
                blank=True,
                help_text="Primary map location for this project",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="primary_projects",
                to="locations.location",
            ),
        ),
    ]
