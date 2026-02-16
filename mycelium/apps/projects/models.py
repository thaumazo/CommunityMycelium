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
    owners = models.ManyToManyField(
        User,
        related_name="owned_projects",
        blank=True,
        help_text="Users who can respond to relationship proposals for this project"
    )
    admins = models.ManyToManyField(
        User,
        related_name="admin_projects",
        blank=True,
        help_text="Users who can respond to relationship proposals for this project"
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


class ProjectCapitalIn(models.Model):
    """
    Through model for project-capital_in relationship.
    Stories attach to this to be project-specific.
    """
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='project_capital_in_relationships'
    )
    capital = models.ForeignKey(
        'capitals.Capital',
        on_delete=models.CASCADE,
        related_name='project_in_relationships'
    )
    
    permissions = GenericRelation(ObjectPermission)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['project', 'capital']
        permissions = [
            ("delegate_projectcapitalin", "Can delegate project capital in"),
        ]
    
    def __str__(self):
        return f"{self.project.title} - {self.capital.title} (In)"


class ProjectCapitalOut(models.Model):
    """
    Through model for project-capital_out relationship.
    Stories attach to this to be project-specific.
    """
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='project_capital_out_relationships'
    )
    capital = models.ForeignKey(
        'capitals.Capital',
        on_delete=models.CASCADE,
        related_name='project_out_relationships'
    )
    
    permissions = GenericRelation(ObjectPermission)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['project', 'capital']
        permissions = [
            ("delegate_projectcapitalout", "Can delegate project capital out"),
        ]
    
    def __str__(self):
        return f"{self.project.title} - {self.capital.title} (Out)"
