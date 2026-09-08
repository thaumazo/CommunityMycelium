from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from apps.acl.models import ObjectPermission

User = get_user_model()


class Commons(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    bioregion = models.ForeignKey(
        "bioregions.Bioregion",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="commons",
        help_text="Bioregion this commons is usually linked to. Leave blank for a non-regional commons.",
    )

    agreements_url = models.URLField(
        blank=True,
        null=True,
        help_text="Link to a Google Doc specifying the rights and responsibilities of commons membership.",
    )

    owners = models.ManyToManyField(
        User,
        related_name="owned_commons",
        blank=True,
        help_text="Superadmin-assigned users who can manage this commons' admins.",
    )
    admins = models.ManyToManyField(
        User,
        related_name="admin_commons",
        blank=True,
        help_text="Users who can manage this commons' members, applications and invites.",
    )
    members = models.ManyToManyField(
        User,
        related_name="member_commons",
        blank=True,
        help_text="Users who are members of this commons.",
    )

    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="commons_created"
    )
    permissions = GenericRelation(ObjectPermission)

    view_members = models.BooleanField(
        default=False,
        help_text="Any authenticated member can view this commons.",
    )
    view_public = models.BooleanField(
        default=False,
        help_text="Public (unauthenticated) users can view this commons.",
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "commons"
        permissions = [
            ("delegate_commons", "Can delegate commons"),
        ]


class CommonsApplication(models.Model):
    """A user's self-service request to join a commons as a member."""

    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_DECLINED = "declined"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_DECLINED, "Declined"),
    ]

    commons = models.ForeignKey(Commons, on_delete=models.CASCADE, related_name="applications")
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commons_applications")
    note = models.TextField(blank=True, null=True, help_text="Optional note from the applicant.")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING)
    decided_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="commons_applications_decided"
    )
    decided_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["commons", "applicant"],
                condition=models.Q(status="pending"),
                name="unique_pending_commons_application",
            )
        ]

    def __str__(self):
        return f"{self.applicant} -> {self.commons} ({self.status})"


class CommonsInvite(models.Model):
    """An owner/admin-initiated invite for an existing user to join a commons."""

    STATUS_PENDING = "pending"
    STATUS_ACCEPTED = "accepted"
    STATUS_DECLINED = "declined"
    STATUS_REVOKED = "revoked"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_DECLINED, "Declined"),
        (STATUS_REVOKED, "Revoked"),
    ]

    commons = models.ForeignKey(Commons, on_delete=models.CASCADE, related_name="invites")
    invited_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commons_invites")
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="commons_invites_sent")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["commons", "invited_user"],
                condition=models.Q(status="pending"),
                name="unique_pending_commons_invite",
            )
        ]

    def __str__(self):
        return f"{self.commons} -> {self.invited_user} ({self.status})"
