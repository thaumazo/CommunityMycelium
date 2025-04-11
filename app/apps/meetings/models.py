from django.db import models
from django.contrib.auth import get_user_model
from apps.core.permissions import PermissionService

User = get_user_model()


class Meeting(models.Model):
    title = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="meetings"
    )

    def __str__(self):
        return self.title

    def can_edit(self, user):
        """Check if user can edit this meeting"""
        return PermissionService.can_edit_meeting(user, self)

    def can_delete(self, user):
        """Check if user can delete this meeting"""
        return PermissionService.can_delete_meeting(user, self)
