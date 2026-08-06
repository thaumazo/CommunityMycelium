from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from apps.acl.models import ObjectPermission

User = get_user_model()


class Project(models.Model):
    TIME_PRECISION_NONE = "none"
    TIME_PRECISION_POINT = "point"
    TIME_PRECISION_RANGE = "range"

    TIME_PRECISION_CHOICES = [
        (TIME_PRECISION_NONE, "No time specified"),
        (TIME_PRECISION_POINT, "Single point in time"),
        (TIME_PRECISION_RANGE, "Time range"),
    ]

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
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
        help_text="Optional parent move for creating nested sub-moves.",
    )
    time_precision = models.CharField(
        max_length=20,
        choices=TIME_PRECISION_CHOICES,
        default=TIME_PRECISION_NONE,
        help_text="Whether this project is anchored at a point in time or a range.",
    )
    project_start_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Optional start time for this project",
    )
    project_end_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Optional end time for this project (for ranges)",
    )
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
    locations = models.ManyToManyField(
        "locations.Location",
        related_name="projects",
        blank=True,
        help_text="Locations this project is connected to",
    )
    primary_location = models.ForeignKey(
        "locations.Location",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="primary_projects",
        help_text="Primary map location for this project",
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

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.parent_id and self.pk and self.parent_id == self.pk:
            raise ValidationError("A move cannot be its own parent.")

        ancestor = self.parent
        while ancestor is not None:
            if self.pk and ancestor.pk == self.pk:
                raise ValidationError("Parent relationship creates a cycle.")
            ancestor = ancestor.parent

        if self.project_end_at and not self.project_start_at:
            raise ValidationError("project_start_at is required when project_end_at is set.")
        if self.project_start_at and self.project_end_at and self.project_end_at < self.project_start_at:
            raise ValidationError("project_end_at must be after project_start_at.")

        if self.time_precision == self.TIME_PRECISION_POINT and self.project_end_at:
            raise ValidationError("Point-in-time projects should not set project_end_at.")
        if self.time_precision == self.TIME_PRECISION_RANGE and not self.project_end_at:
            raise ValidationError("Range projects require project_end_at.")
        if self.time_precision == self.TIME_PRECISION_NONE and (self.project_start_at or self.project_end_at):
            raise ValidationError("Set time_precision to point or range when time fields are used.")

    class Meta:
        verbose_name = "Move"
        verbose_name_plural = "Moves"
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
