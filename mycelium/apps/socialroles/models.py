from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from apps.acl.models import ObjectPermission

User = get_user_model()


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


class UserSocialrole(models.Model):
    """
    Through model for user-socialrole relationship.
    Stories attach to this to be user-specific.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_socialrole_relationships'
    )
    socialrole = models.ForeignKey(
        Socialrole,
        on_delete=models.CASCADE,
        related_name='user_relationships'
    )
    
    permissions = GenericRelation(ObjectPermission)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'socialrole']
        permissions = [
            ("delegate_usersocialrole", "Can delegate user social role"),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.socialrole.title}"
