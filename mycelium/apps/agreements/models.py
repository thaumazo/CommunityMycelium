from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from apps.acl.models import ObjectPermission

User = get_user_model()


class Agreement(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    url = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="agreements"
    )
    permissions = GenericRelation(ObjectPermission)

    def __str__(self):
        return self.title

    class Meta:
        permissions = [
            ("delegate_agreement", "Can delegate agreement"),
        ]
