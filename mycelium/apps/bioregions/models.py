from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from apps.acl.models import ObjectPermission

User = get_user_model()


class Bioregion(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    parent_region = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="child_regions",
    )

    picture = models.ImageField(
        upload_to='bioregion_pictures/',
        blank=True,
        null=True,
        help_text="Representative image for this bioregion"
    )
    picture_thumbnail = models.ImageField(
        upload_to='bioregion_pictures/thumbnails/',
        blank=True,
        null=True,
        editable=False,
        help_text="Automatically generated thumbnail"
    )

    location = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Location or address of this bioregion"
    )
    latitude = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Latitude coordinate"
    )
    longitude = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Longitude coordinate"
    )
    radius_km = models.FloatField(
        blank=True,
        null=True,
        help_text="Radius of the bioregion in kilometers"
    )

    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="bioregions"
    )

    admins = models.ManyToManyField(
        User,
        related_name="admin_bioregions",
        blank=True,
        help_text="Users who can manage this bioregion's members and visibility settings",
    )
    owners = models.ManyToManyField(
        User,
        related_name="owned_bioregions",
        blank=True,
        help_text="Superadmin-assigned users who can manage this bioregion's admins",
    )
    members = models.ManyToManyField(
        User,
        related_name="member_bioregions",
        blank=True,
        help_text="Users who are members of this bioregion",
    )

    view_members = models.BooleanField(
        default=False,
        help_text="Any authenticated member can view this bioregion. Users connected to the bioregion can always view it regardless of this setting.",
    )
    view_public = models.BooleanField(
        default=False,
        help_text="Public (unauthenticated) users can view this bioregion.",
    )

    visible_to_commons = models.ManyToManyField(
        "commons.Commons",
        related_name="visible_bioregions",
        blank=True,
        help_text="Members of these commons can view this bioregion, regardless of view_members/view_public.",
    )

    permissions = GenericRelation(ObjectPermission)

    def __str__(self):
        return self.title

    class Meta:
        permissions = [
            ("delegate_bioregion", "Can delegate bioregion"),
        ]
