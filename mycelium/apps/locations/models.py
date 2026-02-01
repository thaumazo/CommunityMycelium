from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from apps.acl.models import ObjectPermission

User = get_user_model()


class Location(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    bioregions = models.ManyToManyField(
        "bioregions.Bioregion",
        related_name="locations",
        blank=True,
        help_text="Bioregions this location is connected to",
    )

    picture = models.ImageField(
        upload_to="location_pictures/",
        blank=True,
        null=True,
        help_text="Representative image for this location",
    )
    picture_thumbnail = models.ImageField(
        upload_to="location_pictures/thumbnails/",
        blank=True,
        null=True,
        editable=False,
        help_text="Automatically generated thumbnail",
    )

    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="locations"
    )
    permissions = GenericRelation(ObjectPermission)

    view_members = models.BooleanField(
        default=False,
        help_text="Authenticated members can view this location.",
    )

    view_public = models.BooleanField(
        default=False,
        help_text="Public (unauthenticated) users can view this location.",
    )

    def __str__(self):
        return self.title

    class Meta:
        permissions = [
            ("delegate_location", "Can delegate location"),
        ]


class LocationCapital(models.Model):
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name="location_capital_relationships",
    )
    capital = models.ForeignKey(
        "capitals.Capital",
        on_delete=models.CASCADE,
        related_name="location_relationships",
    )

    permissions = GenericRelation(ObjectPermission)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["location", "capital"]
        permissions = [
            ("delegate_locationcapital", "Can delegate location capital"),
        ]

    def __str__(self):
        return f"{self.location.title} - {self.capital.title}"
