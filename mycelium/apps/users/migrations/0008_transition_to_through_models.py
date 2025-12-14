# Generated manually to transition M2M fields to use through models

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_user_is_approved'),
        ('socialroles', '0003_migrate_m2m_data'),
        ('metacrisis_facets', '0003_migrate_m2m_data'),
        ('maladaptives', '0003_migrate_m2m_data'),
    ]

    operations = [
        # Use SeparateDatabaseAndState to handle the model state change
        # without actually altering the database (since through tables already exist)
        migrations.SeparateDatabaseAndState(
            state_operations=[
                # Remove old M2M fields from model state
                migrations.RemoveField(
                    model_name='user',
                    name='user_socialroles',
                ),
                migrations.RemoveField(
                    model_name='user',
                    name='user_metacrisis_facets',
                ),
                migrations.RemoveField(
                    model_name='user',
                    name='user_maladaptives',
                ),
                # Add new M2M fields with through models
                migrations.AddField(
                    model_name='user',
                    name='user_socialroles',
                    field=models.ManyToManyField(
                        blank=True,
                        related_name='users',
                        through='socialroles.UserSocialrole',
                        to='socialroles.socialrole'
                    ),
                ),
                migrations.AddField(
                    model_name='user',
                    name='user_metacrisis_facets',
                    field=models.ManyToManyField(
                        blank=True,
                        related_name='users',
                        through='metacrisis_facets.UserMetacrisisFacet',
                        to='metacrisis_facets.metacrisis_facet'
                    ),
                ),
                migrations.AddField(
                    model_name='user',
                    name='user_maladaptives',
                    field=models.ManyToManyField(
                        blank=True,
                        related_name='users',
                        through='maladaptives.UserMaladaptive',
                        to='maladaptives.maladaptive'
                    ),
                ),
            ],
            database_operations=[
                # Drop old M2M tables in database
                migrations.RunSQL(
                    sql="DROP TABLE IF EXISTS users_user_user_socialroles",
                    reverse_sql="CREATE TABLE users_user_user_socialroles (id bigint NOT NULL AUTO_INCREMENT, user_id bigint NOT NULL, socialrole_id bigint NOT NULL, PRIMARY KEY (id), UNIQUE KEY users_user_user_socialroles_user_id_socialrole_id_2b11150b_uniq (user_id, socialrole_id))",
                ),
                migrations.RunSQL(
                    sql="DROP TABLE IF EXISTS users_user_user_metacrisis_facets",
                    reverse_sql="CREATE TABLE users_user_user_metacrisis_facets (id bigint NOT NULL AUTO_INCREMENT, user_id bigint NOT NULL, metacrisis_facet_id bigint NOT NULL, PRIMARY KEY (id), UNIQUE KEY users_user_user_metacris_user_id_metacrisis_facet_16d329e8_uniq (user_id, metacrisis_facet_id))",
                ),
                migrations.RunSQL(
                    sql="DROP TABLE IF EXISTS users_user_user_maladaptives",
                    reverse_sql="CREATE TABLE users_user_user_maladaptives (id bigint NOT NULL AUTO_INCREMENT, user_id bigint NOT NULL, maladaptive_id bigint NOT NULL, PRIMARY KEY (id), UNIQUE KEY users_user_user_maladapt_user_id_maladaptive_id_a050f2b1_uniq (user_id, maladaptive_id))",
                ),
            ],
        ),
    ]
