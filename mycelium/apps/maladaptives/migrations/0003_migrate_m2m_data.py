# Generated manually to migrate M2M data to through model

from django.db import migrations


def migrate_maladaptive_data(apps, schema_editor):
    """Copy data from old M2M table to new through model table."""
    db_alias = schema_editor.connection.alias
    
    # Use raw SQL to copy data
    with schema_editor.connection.cursor() as cursor:
        # Copy data from old M2M table to through model table
        cursor.execute("""
            INSERT IGNORE INTO maladaptives_usermaladaptive (user_id, maladaptive_id, created_at)
            SELECT user_id, maladaptive_id, NOW()
            FROM users_user_user_maladaptives
        """)


def reverse_migration(apps, schema_editor):
    """Reverse migration - copy data back."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('maladaptives', '0002_usermaladaptive'),
        ('users', '0007_user_is_approved'),
    ]

    operations = [
        migrations.RunPython(migrate_maladaptive_data, reverse_migration),
    ]
