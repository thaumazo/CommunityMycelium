from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("bioregions", "0001_initial"),
        ("users", "0014_user_invites_and_primary_location"),
    ]

    operations = [
        migrations.AddField(
            model_name="userinvite",
            name="bioregion",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="invites",
                to="bioregions.bioregion",
            ),
        ),
    ]
