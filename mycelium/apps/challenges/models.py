from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from apps.acl.models import ObjectPermission
from apps.metacrisis_facets.models import Metacrisis_facet
from apps.bioregions.models import Bioregion
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Challenge(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    parent_region = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="child_regions",
    )

    related_facet = models.ForeignKey(
        Metacrisis_facet,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="challenges",
    )

    related_bioregion = models.ForeignKey(
        Bioregion,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="challenges",
    )

    level = models.IntegerField(
        default=0,
        validators=[
            MinValueValidator(-100),
            MaxValueValidator(100),
        ],
    )

    location = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="challenges"
    )
    permissions = GenericRelation(ObjectPermission)

    def __str__(self):
        return self.title

    class Meta:
        permissions = [
            ("delegate_challenge", "Can delegate challenge"),
        ]
