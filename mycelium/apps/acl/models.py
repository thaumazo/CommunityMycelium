from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class ObjectPermission(models.Model):
    ACTION_CHOICES = [
        ("add", "Add"),
        ("change", "Change"),
        ("delete", "Delete"),
        ("view", "View"),
        ("delegate", "Delegate"),  # Ability to grant/revoke permissions
    ]

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)

    # Generic foreign key to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        unique_together = ("user", "action", "content_type", "object_id")

    def __str__(self):
        return f"{self.user.username} can {self.action} {self.content_object}"
