from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0015_userinvite_bioregion"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="alternate_deck",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Optional alternate deck slug (e.g. 'moore') used for deck image overrides.",
                max_length=64,
            ),
        ),
    ]
