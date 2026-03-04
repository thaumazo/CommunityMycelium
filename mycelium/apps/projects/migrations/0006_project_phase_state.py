from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0005_project_bioregions'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='phase',
            field=models.CharField(choices=[('idea', 'Idea'), ('scoping', 'Scoping'), ('ready', 'Ready'), ('active', 'Active'), ('review', 'Review'), ('complete', 'Complete')], default='idea', help_text='Lifecycle phase from idea through completion.', max_length=20),
        ),
        migrations.AddField(
            model_name='project',
            name='state',
            field=models.CharField(choices=[('planned', 'Planned'), ('active', 'Active'), ('on_hold', 'On Hold'), ('blocked', 'Blocked')], default='active', help_text='Current operating state such as active, planned, on hold, or blocked.', max_length=20),
        ),
    ]
