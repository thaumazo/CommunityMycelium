from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from apps.acl.models import ObjectPermission

User = get_user_model()


class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    members = models.ManyToManyField(
        User,
        related_name="members_projects",
        blank=True,
        help_text="Users who are members of this project"
    )
    url = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="projects"
    )
    permissions = GenericRelation(ObjectPermission)

    view_members = models.BooleanField(
        default=False,
        help_text="Authenticated members can view this project.",
    )

    view_public = models.BooleanField(
        default=False,
        help_text="Public (unauthenticated) users can view this project.",
    )

    def __str__(self):
        return self.title

    class Meta:
        permissions = [
            ("delegate_project", "Can delegate project"),
        ]
