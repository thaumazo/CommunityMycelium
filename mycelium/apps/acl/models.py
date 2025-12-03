from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class ModelPermission(models.Model):
    """
    Model-level permissions for individual users.
    Grants permission to perform an action on all objects of a given model type.
    """
    ACTION_CHOICES = [
        ("add", "Add"),
        ("change", "Change"),
        ("delete", "Delete"),
        ("view", "View"),
        ("delegate", "Delegate"),  # Ability to grant/revoke permissions
    ]

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "action", "content_type")
        verbose_name = "Model Permission"
        verbose_name_plural = "Model Permissions"

    def __str__(self):
        model_name = self.content_type.model_class()._meta.verbose_name if self.content_type.model_class() else self.content_type.model
        return f"{self.user.username} can {self.action} all {model_name}"


class ObjectPermission(models.Model):
    """
    Object-level permissions for individual users.
    Grants permission to perform an action on a specific object instance.
    """
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
        verbose_name = "Object Permission"
        verbose_name_plural = "Object Permissions"

    def __str__(self):
        return f"{self.user.username} can {self.action} {self.content_object}"
