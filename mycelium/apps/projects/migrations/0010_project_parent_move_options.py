from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0009_project_time_precision_project_start_at_project_end_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                help_text="Optional parent move for creating nested sub-moves.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="children",
                to="projects.project",
            ),
        ),
        migrations.AlterModelOptions(
            name="project",
            options={
                "permissions": [("delegate_project", "Can delegate project")],
                "verbose_name": "Move",
                "verbose_name_plural": "Moves",
            },
        ),
    ]
