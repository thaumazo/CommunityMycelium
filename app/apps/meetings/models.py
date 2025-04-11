from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

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

    def can_view(self, user):
        if user.is_superuser:
            return True
        return user.groups.filter(name__in=["viewer", "editor", "admin"]).exists()

    def can_edit(self, user):
        if user.is_superuser:
            return True
        return user.groups.filter(name__in=["editor", "admin"]).exists()

    def can_delete(self, user):
        if user.is_superuser:
            return True
        return user.groups.filter(name="admin").exists()
