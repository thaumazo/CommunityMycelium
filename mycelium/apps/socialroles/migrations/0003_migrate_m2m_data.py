# Generated manually to migrate M2M data to through model

from django.db import migrations


def migrate_socialrole_data(apps, schema_editor):
    """Copy data from old M2M table to new through model table."""
    db_alias = schema_editor.connection.alias
    
    # Use raw SQL to copy data
    with schema_editor.connection.cursor() as cursor:
        # Copy data from old M2M table to through model table
        cursor.execute("""
            INSERT IGNORE INTO socialroles_usersocialrole (user_id, socialrole_id, created_at)
            SELECT user_id, socialrole_id, NOW()
            FROM users_user_user_socialroles
        """)


def reverse_migration(apps, schema_editor):
    """Reverse migration - copy data back."""
    # We don't need to do anything on reverse since the old table will be recreated
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('socialroles', '0002_usersocialrole'),
        ('users', '0007_user_is_approved'),
    ]

    operations = [
        migrations.RunPython(migrate_socialrole_data, reverse_migration),
    ]
