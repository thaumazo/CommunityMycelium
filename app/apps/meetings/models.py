from django.db import models
from ..orgs.models import Organization
from django.contrib.auth import get_user_model

User = get_user_model()


class Meeting(models.Model):
    title = models.CharField(max_length=255)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="meetings"
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="meetings"
    )
