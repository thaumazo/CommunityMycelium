from django.db import migrations, models


def copy_existing_parents(apps, schema_editor):
    Project = apps.get_model("projects", "Project")
    through_model = Project.parents.through
    links = [
        through_model(from_project_id=project.pk, to_project_id=project.parent_id)
        for project in Project.objects.exclude(parent_id=None)
    ]
    through_model.objects.bulk_create(links, ignore_conflicts=True)


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0012_orientation_move_steps"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="parents",
            field=models.ManyToManyField(
                blank=True,
                help_text="Optional parent moves for creating nested sub-moves.",
                related_name="children",
                symmetrical=False,
                to="projects.project",
            ),
        ),
        migrations.RunPython(copy_existing_parents, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="project",
            name="parent",
        ),
    ]
