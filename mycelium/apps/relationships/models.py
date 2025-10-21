from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from apps.acl.models import ObjectPermission

User = get_user_model()


class Relationship(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    resolutions = models.ManyToManyField(
         'resolutions.Resolution',  # 'app_label.ModelName'
        related_name="relationship_resolutions",
        blank=True,
        help_text="resolutions required for this relationship"
    )
    url = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="relationships"
    )
    permissions = GenericRelation(ObjectPermission)

    def __str__(self):
        return self.title

    class Meta:
        permissions = [
            ("delegate_relationship", "Can delegate relationship"),
        ]
