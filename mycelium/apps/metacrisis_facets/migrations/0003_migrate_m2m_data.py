# Generated manually to migrate M2M data to through model

from django.db import migrations


def migrate_metacrisis_facet_data(apps, schema_editor):
    """Copy data from old M2M table to new through model table."""
    db_alias = schema_editor.connection.alias
    
    # Use raw SQL to copy data
    with schema_editor.connection.cursor() as cursor:
        # Copy data from old M2M table to through model table
        cursor.execute("""
            INSERT IGNORE INTO metacrisis_facets_usermetacrisisfacet (user_id, metacrisis_facet_id, created_at)
            SELECT user_id, metacrisis_facet_id, NOW()
            FROM users_user_user_metacrisis_facets
        """)


def reverse_migration(apps, schema_editor):
    """Reverse migration - copy data back."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('metacrisis_facets', '0002_usermetacrisisfacet'),
        ('users', '0007_user_is_approved'),
    ]

    operations = [
        migrations.RunPython(migrate_metacrisis_facet_data, reverse_migration),
    ]
