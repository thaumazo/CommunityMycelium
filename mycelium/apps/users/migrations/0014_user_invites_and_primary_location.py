from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("locations", "0002_location_bioregions"),
        ("users", "0013_user_ai_transcript_processing"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="invite_role",
            field=models.CharField(
                choices=[("none", "None"), ("invite", "Can Invite"), ("approve", "Can Approve")],
                default="none",
                help_text="Invitation capability: none, can invite, or can approve invitees.",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="invited_by_confirmed_at",
            field=models.DateTimeField(
                blank=True,
                help_text="When the invited_by relationship was confirmed by an approver.",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="primary_location",
            field=models.ForeignKey(
                blank=True,
                help_text="Primary map location for this person.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="primary_users",
                to="locations.location",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="user_locations",
            field=models.ManyToManyField(
                blank=True,
                help_text="Locations connected to this person.",
                related_name="users",
                to="locations.location",
            ),
        ),
        migrations.CreateModel(
            name="UserInvite",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("token", models.CharField(max_length=64, unique=True)),
                ("invited_email", models.EmailField(blank=True, max_length=254, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("registered", "Registered"),
                            ("approved", "Approved"),
                            ("revoked", "Revoked"),
                        ],
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("approved_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "approved_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="approved_invites",
                        to="users.user",
                    ),
                ),
                (
                    "invited_user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="received_invites",
                        to="users.user",
                    ),
                ),
                (
                    "inviter",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sent_invites",
                        to="users.user",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
