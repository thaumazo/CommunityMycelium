from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from apps.acl.models import ObjectPermission

User = get_user_model()


class Meeting(models.Model):
    title = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    attending = models.ManyToManyField(
        User,
        related_name="attending_meetings",
        blank=True,
        help_text="Users who are attending this meeting"
    )
    url = models.TextField(blank=True, null=True)
    transcript = models.TextField(
        blank=True, null=True, help_text="Optional transcript of the meeting"
    )
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="meetings"
    )
    permissions = GenericRelation(ObjectPermission)

    def __str__(self):
        return self.title

    class Meta:
        permissions = [
            ("delegate_meeting", "Can delegate meeting"),
        ]
