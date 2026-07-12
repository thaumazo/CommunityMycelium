from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("locations", "0002_location_bioregions"),
        ("communities", "0006_community_owners_admins"),
    ]

    operations = [
        migrations.AddField(
            model_name="community",
            name="locations",
            field=models.ManyToManyField(
                blank=True,
                help_text="Locations this community is connected to",
                related_name="communities",
                to="locations.location",
            ),
        ),
        migrations.AddField(
            model_name="community",
            name="primary_location",
            field=models.ForeignKey(
                blank=True,
                help_text="Primary map location for this community",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="primary_communities",
                to="locations.location",
            ),
        ),
    ]
