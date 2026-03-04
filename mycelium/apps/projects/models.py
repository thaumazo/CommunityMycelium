from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from apps.acl.models import ObjectPermission

User = get_user_model()


class Project(models.Model):
    PHASE_UNKNOWN = "unknown"
    PHASE_IDEA = "idea"
    PHASE_SCOPING = "scoping"
    PHASE_READY = "ready"
    PHASE_ACTIVE = "active"
    PHASE_REVIEW = "review"
    PHASE_COMPLETE = "complete"

    PHASE_CHOICES = [
        (PHASE_UNKNOWN, "Unknown"),
        (PHASE_IDEA, "Idea"),
        (PHASE_SCOPING, "Scoping"),
        (PHASE_READY, "Ready"),
        (PHASE_ACTIVE, "Active"),
        (PHASE_REVIEW, "Review"),
        (PHASE_COMPLETE, "Complete"),
    ]

    STATE_UNKNOWN = "unknown"
    STATE_PLANNED = "planned"
    STATE_ACTIVE = "active"
    STATE_ON_HOLD = "on_hold"
    STATE_BLOCKED = "blocked"

    STATE_CHOICES = [
        (STATE_UNKNOWN, "Unknown"),
        (STATE_PLANNED, "Planned"),
        (STATE_ACTIVE, "Active"),
        (STATE_ON_HOLD, "On Hold"),
        (STATE_BLOCKED, "Blocked"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    phase = models.CharField(
        max_length=20,
        choices=PHASE_CHOICES,
        default=PHASE_UNKNOWN,
        help_text="Lifecycle phase from idea through completion.",
    )
    state = models.CharField(
        max_length=20,
        choices=STATE_CHOICES,
        default=STATE_UNKNOWN,
        help_text="Current operating state such as active, planned, on hold, or blocked.",
    )
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
    bioregions = models.ManyToManyField(
        "bioregions.Bioregion",
        related_name="projects",
        blank=True,
        help_text="Bioregions this project is connected to"
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
