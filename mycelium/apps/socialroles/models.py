from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from apps.acl.models import ObjectPermission

class Socialrole(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image_path = models.CharField(max_length=255, blank=True, help_text="Relative path to static image (e.g. 'img/roles/weavers.webp')")    
    permissions = GenericRelation(ObjectPermission)

    def __str__(self):
        return self.title

    class Meta:
        permissions = [
            ("delegate_socialrole", "Can delegate social role"),
        ]
