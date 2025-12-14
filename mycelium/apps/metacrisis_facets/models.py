from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from apps.acl.models import ObjectPermission

User = get_user_model()


class Metacrisis_facet(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image_path = models.CharField(max_length=255, blank=True, help_text="Relative path to static image (e.g. 'img/roles/weavers.webp')")    
    permissions = GenericRelation(ObjectPermission)

    def __str__(self):
        return self.title

    class Meta:
        permissions = [
            ("delegate_metacrisis_facet", "Can delegate metacrisis facets"),
        ]


class UserMetacrisisFacet(models.Model):
    """
    Through model for user-metacrisis_facet relationship.
    Stories attach to this to be user-specific.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_metacrisis_facet_relationships'
    )
    metacrisis_facet = models.ForeignKey(
        Metacrisis_facet,
        on_delete=models.CASCADE,
        related_name='user_relationships'
    )
    
    permissions = GenericRelation(ObjectPermission)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'metacrisis_facet']
        permissions = [
            ("delegate_usermetacrisisfacet", "Can delegate user metacrisis facet"),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.metacrisis_facet.title}"
