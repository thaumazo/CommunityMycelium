from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from apps.acl.models import ObjectPermission

User = get_user_model()


class Relationship(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    resolutions = models.ManyToManyField(
         'resolutions.Resolution',  # 'app_label.ModelName'
        related_name="relationship_resolutions",
        blank=True,
        help_text="resolutions required for this relationship"
    )
    url = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="relationships"
    )
    permissions = GenericRelation(ObjectPermission)

    def __str__(self):
        return self.title

    class Meta:
        permissions = [
            ("delegate_relationship", "Can delegate relationship"),
        ]


class RelationshipProposal(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"
        COUNTERED = "countered", "Countered"

    initiator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="initiated_relationship_proposals",
    )
    from_person = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_relationship_proposals",
        null=True,
        blank=True,
    )
    from_community = models.ForeignKey(
        "communities.Community",
        on_delete=models.CASCADE,
        related_name="sent_relationship_proposals",
        null=True,
        blank=True,
    )
    from_project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="sent_relationship_proposals",
        null=True,
        blank=True,
    )
    to_person = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_relationship_proposals",
        null=True,
        blank=True,
    )
    to_community = models.ForeignKey(
        "communities.Community",
        on_delete=models.CASCADE,
        related_name="received_relationship_proposals",
        null=True,
        blank=True,
    )
    to_project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="received_relationship_proposals",
        null=True,
        blank=True,
    )
    relationship_type = models.ForeignKey(
        "relationships.Relationship",
        on_delete=models.CASCADE,
        related_name="proposals",
    )
    note = models.TextField(blank=True, null=True)
    resolution = models.ForeignKey(
        "resolutions.Resolution",
        on_delete=models.CASCADE,
        related_name="relationship_proposals",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    counter_parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="counters",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        from_targets = [self.from_person, self.from_community, self.from_project]
        to_targets = [self.to_person, self.to_community, self.to_project]
        if sum(1 for target in from_targets if target is not None) != 1:
            raise ValidationError("Exactly one from-party must be set for a relationship proposal.")
        if sum(1 for target in to_targets if target is not None) != 1:
            raise ValidationError("Exactly one to-party must be set for a relationship proposal.")

    def get_from_party(self):
        return self.from_person or self.from_community or self.from_project

    def get_to_party(self):
        return self.to_person or self.to_community or self.to_project

    def get_from_label(self):
        party = self.get_from_party()
        return party.title if hasattr(party, "title") else party.get_full_name()

    def get_to_label(self):
        party = self.get_to_party()
        return party.title if hasattr(party, "title") else party.get_full_name()

    def is_recipient(self, user):
        if not user or not user.is_authenticated:
            return False
        if self.to_person_id:
            return self.to_person_id == user.id
        if self.to_community_id:
            return (
                self.to_community.owners.filter(id=user.id).exists()
                or self.to_community.admins.filter(id=user.id).exists()
            )
        if self.to_project_id:
            return (
                self.to_project.owners.filter(id=user.id).exists()
                or self.to_project.admins.filter(id=user.id).exists()
            )
        return False

    def can_view(self, user):
        return self.initiator_id == getattr(user, "id", None) or self.is_recipient(user)

    def __str__(self):
        return f"{self.get_from_label()} -> {self.get_to_label()}"


class RelationshipProposalResponse(models.Model):
    class Action(models.TextChoices):
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"
        COUNTERED = "countered", "Countered"

    proposal = models.ForeignKey(
        RelationshipProposal,
        on_delete=models.CASCADE,
        related_name="responses",
    )
    responder = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="relationship_proposal_responses",
    )
    action = models.CharField(max_length=20, choices=Action.choices)
    note = models.TextField(blank=True, null=True)
    counter_proposal = models.ForeignKey(
        RelationshipProposal,
        on_delete=models.SET_NULL,
        related_name="counter_responses",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.responder} {self.action}"


class RelationshipInstance(models.Model):
    relationship_type = models.ForeignKey(
        "relationships.Relationship",
        on_delete=models.CASCADE,
        related_name="instances",
    )
    resolution = models.ForeignKey(
        "resolutions.Resolution",
        on_delete=models.CASCADE,
        related_name="relationship_instances",
    )
    initiator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="initiated_relationships",
    )
    from_person = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_relationships",
        null=True,
        blank=True,
    )
    from_community = models.ForeignKey(
        "communities.Community",
        on_delete=models.CASCADE,
        related_name="sent_relationship_instances",
        null=True,
        blank=True,
    )
    from_project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="sent_relationship_instances",
        null=True,
        blank=True,
    )
    to_person = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_relationships",
        null=True,
        blank=True,
    )
    to_community = models.ForeignKey(
        "communities.Community",
        on_delete=models.CASCADE,
        related_name="received_relationship_instances",
        null=True,
        blank=True,
    )
    to_project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="received_relationship_instances",
        null=True,
        blank=True,
    )
    title_override = models.CharField(max_length=255, blank=True, null=True)
    description_override = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_relationship_instances",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()
        from_targets = [self.from_person, self.from_community, self.from_project]
        to_targets = [self.to_person, self.to_community, self.to_project]
        if sum(1 for target in from_targets if target is not None) != 1:
            raise ValidationError("Exactly one from-party must be set for a relationship instance.")
        if sum(1 for target in to_targets if target is not None) != 1:
            raise ValidationError("Exactly one to-party must be set for a relationship instance.")

    def display_title(self):
        return self.title_override or self.relationship_type.title

    def display_description(self):
        return self.description_override or self.relationship_type.description

    def __str__(self):
        return self.display_title()
