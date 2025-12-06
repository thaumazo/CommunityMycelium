from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from apps.acl.models import ObjectPermission

User = get_user_model()


class Community(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    members = models.ManyToManyField(
        User,
        related_name="members_communities",
        blank=True,
        help_text="Users who are members of this community"
    )
    bioregions = models.ManyToManyField(
        "bioregions.Bioregion",
        related_name="communities",
        blank=True,
        help_text="Bioregions this community is connected to"
    )
    url = models.TextField(blank=True, null=True)
    
    picture = models.ImageField(
        upload_to='community_pictures/',
        blank=True,
        null=True,
        help_text="Representative image for this community"
    )
    picture_thumbnail = models.ImageField(
        upload_to='community_pictures/thumbnails/',
        blank=True,
        null=True,
        editable=False,
        help_text="Automatically generated thumbnail"
    )
    
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="communities"
    )
    permissions = GenericRelation(ObjectPermission)

    view_members = models.BooleanField(
        default=False,
        help_text="Authenticated members can view this community.",
    )

    view_public = models.BooleanField(
        default=False,
        help_text="Public (unauthenticated) users can view this community.",
    )

    def __str__(self):
        return self.title

    class Meta:
        permissions = [
            ("delegate_community", "Can delegate community"),
        ]
