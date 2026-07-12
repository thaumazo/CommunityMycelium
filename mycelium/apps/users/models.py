from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    INVITE_ROLE_NONE = "none"
    INVITE_ROLE_INVITE = "invite"
    INVITE_ROLE_APPROVE = "approve"

    INVITE_ROLE_CHOICES = [
        (INVITE_ROLE_NONE, "None"),
        (INVITE_ROLE_INVITE, "Can Invite"),
        (INVITE_ROLE_APPROVE, "Can Approve"),
    ]

    full_name = models.CharField(max_length=255, blank=True)

    user_location = models.CharField(max_length=255, blank=True, null=True)

    invited_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="invited_users",
    )

    invited_by_confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the invited_by relationship was confirmed by an approver.",
    )

    invite_role = models.CharField(
        max_length=16,
        choices=INVITE_ROLE_CHOICES,
        default=INVITE_ROLE_NONE,
        help_text="Invitation capability: none, can invite, or can approve invitees.",
    )

    user_locations = models.ManyToManyField(
        "locations.Location",
        blank=True,
        related_name="users",
        help_text="Locations connected to this person.",
    )

    primary_location = models.ForeignKey(
        "locations.Location",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="primary_users",
        help_text="Primary map location for this person.",
    )

    user_bioregions = models.ManyToManyField(
        "bioregions.Bioregion", blank=True, related_name="users"
    )

    user_communities = models.ManyToManyField(
        "communities.Community", blank=True, related_name="users"
    )

    user_projects = models.ManyToManyField(
        "projects.Project", blank=True, related_name="connected_users"
    )

    user_relationships = models.ManyToManyField("relationships.Relationship", blank=True, related_name="users")
    user_socialroles = models.ManyToManyField(
        "socialroles.Socialrole",
        through="socialroles.UserSocialrole",
        blank=True,
        related_name="users"
    )
    user_metacrisis_facets = models.ManyToManyField(
        "metacrisis_facets.Metacrisis_facet",
        through="metacrisis_facets.UserMetacrisisFacet",
        blank=True,
        related_name="users"
    )
    user_maladaptives = models.ManyToManyField(
        "maladaptives.Maladaptive",
        through="maladaptives.UserMaladaptive",
        blank=True,
        related_name="users"
    )

    linked_in = models.URLField(blank=True, null=True)
    
    bio = models.TextField(
        blank=True,
        help_text="User biography or description"
    )

    picture = models.ImageField(
        upload_to='user_pictures/',
        blank=True,
        null=True,
        help_text="Profile picture"
    )
    picture_thumbnail = models.ImageField(
        upload_to='user_pictures/thumbnails/',
        blank=True,
        null=True,
        editable=False,
        help_text="Automatically generated thumbnail"
    )

    # Remove first_name and last_name from the model
    first_name = None
    last_name = None

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.full_name

    def is_admin(self):
        return self.groups.filter(name="Admin").exists()

    view_members = models.BooleanField(
        default=False,
        help_text="Indicates if the user can view members.",
    )

    view_public = models.BooleanField(
        default=False,
        help_text="Indicates if the user can view public content.",
    )

    ai_transcript_processing = models.BooleanField(
        default=False,
        help_text="Allow AI (like GPT in temporary mode) to analyze meeting transcripts to make connections between people and extract useful tasks.",
    )

    is_approved = models.BooleanField(
        default=True,
        help_text="Indicates if the user has been approved by a superuser.",
    )

    class Meta:
        ordering = ['full_name']

    def can_invite(self):
        if self.is_superuser:
            return True
        return self.invite_role in {self.INVITE_ROLE_INVITE, self.INVITE_ROLE_APPROVE}

    def can_approve_people(self):
        if self.is_superuser:
            return True
        return self.invite_role == self.INVITE_ROLE_APPROVE


class UserInvite(models.Model):
    STATUS_PENDING = "pending"
    STATUS_REGISTERED = "registered"
    STATUS_APPROVED = "approved"
    STATUS_REVOKED = "revoked"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_REGISTERED, "Registered"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REVOKED, "Revoked"),
    ]

    token = models.CharField(max_length=64, unique=True)
    inviter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_invites",
    )
    invited_email = models.EmailField(blank=True, null=True)
    invited_user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="received_invites",
    )
    bioregion = models.ForeignKey(
        "bioregions.Bioregion",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="invites",
    )
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING)
    approved_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_invites",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Invite {self.token[:8]} by {self.inviter.username}"


class UserGoogleAuth(models.Model):
    """Store Google OAuth credentials for a user."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="google_auth"
    )
    access_token = models.TextField(
        help_text="Encrypted Google OAuth access token"
    )
    refresh_token = models.TextField(
        blank=True, null=True,
        help_text="Encrypted Google OAuth refresh token"
    )
    token_expiry = models.DateTimeField(
        blank=True, null=True,
        help_text="When the access token expires"
    )
    scopes = models.TextField(
        help_text="Space-separated list of granted OAuth scopes"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Google Auth for {self.user.username}"

    class Meta:
        verbose_name = "User Google Authentication"
        verbose_name_plural = "User Google Authentications"
