from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    full_name = models.CharField(max_length=255, blank=True)

    user_location = models.CharField(max_length=255, blank=True, null=True)

    invited_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="invited_users",
    )

    user_bioregions = models.ManyToManyField(
        "bioregions.Bioregion", blank=True, related_name="users"
    )

    user_communities = models.ManyToManyField(
        "communities.Community", blank=True, related_name="users"
    )

    user_relationships = models.ManyToManyField("relationships.Relationship", blank=True, related_name="users")
    user_socialroles = models.ManyToManyField("socialroles.Socialrole", blank=True, related_name="users")
    user_metacrisis_facets = models.ManyToManyField("metacrisis_facets.Metacrisis_facet", blank=True, related_name="users")
    user_maladaptives = models.ManyToManyField("maladaptives.Maladaptive", blank=True, related_name="users")

    linked_in = models.URLField(blank=True, null=True)

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
