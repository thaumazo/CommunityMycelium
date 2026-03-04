from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0006_project_phase_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='phase',
            field=models.CharField(
                choices=[
                    ('unknown', 'Unknown'),
                    ('idea', 'Idea'),
                    ('scoping', 'Scoping'),
                    ('ready', 'Ready'),
                    ('active', 'Active'),
                    ('review', 'Review'),
                    ('complete', 'Complete'),
                ],
                default='unknown',
                help_text='Lifecycle phase from idea through completion.',
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name='project',
            name='state',
            field=models.CharField(
                choices=[
                    ('unknown', 'Unknown'),
                    ('planned', 'Planned'),
                    ('active', 'Active'),
                    ('on_hold', 'On Hold'),
                    ('blocked', 'Blocked'),
                ],
                default='unknown',
                help_text='Current operating state such as active, planned, on hold, or blocked.',
                max_length=20,
            ),
        ),
    ]
