from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from apps.acl.utils import get_permitted_objects, get_permitted_object, is_permitted
from django.core.exceptions import PermissionDenied
from apps.utils.pagination import paginate_queryset
from apps.communities.models import Community
from apps.projects.models import Project
from apps.users.models import User
from .models import Relationship, RelationshipProposal, RelationshipProposalResponse, RelationshipInstance
from .forms import RelationshipForm, RelationshipProposalForm, RelationshipProposalResponseForm
from apps.utils.form_tokens import get_form_token, validate_form_token
from apps.utils.superuser_fields import attach_creator_field, apply_creator_field


@login_required
def relationship_list_view(request):
    relationships = get_permitted_objects(request.user, "view", Relationship)
    
    # Pagination using helper function
    relationships_page, pagination_data = paginate_queryset(relationships, request, per_page=10)
    
    return render(request, "relationships/relationship_list.html", {
        "relationships": relationships_page,
        "pagination": pagination_data,
    })


@login_required
def relationship_detail_view(request, pk):
    relationship = get_permitted_object(request.user, "view", Relationship, pk)
    return render(request, "relationships/relationship_detail.html", {"relationship": relationship})


@login_required
def relationship_create_view(request):
    if not is_permitted(request.user, "add", "relationships.relationship"):
        raise PermissionDenied

    if request.method == "POST":
        if not validate_form_token(request, 'relationship_create'):
            messages.error(request, "This form has already been submitted. Please don't use the back button after submitting.")
            form = RelationshipForm()
            form_token = get_form_token(request, 'relationship_create')
            return render(request, "relationships/relationship_form.html", {"form": form, "form_token": form_token})
        
        form = RelationshipForm(request.POST)
        if form.is_valid():
            relationship = form.save(commit=False)
            relationship.created_by = request.user
            relationship.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, "Relationship created successfully!")
            return redirect("relationship_detail", pk=relationship.pk)
    else:
        form = RelationshipForm()

    form_token = get_form_token(request, 'relationship_create')
    return render(
        request,
        "relationships/relationship_form.html",
        {"form": form, "form_token": form_token},
    )


@login_required
def relationship_edit_view(request, pk):
    relationship = get_permitted_object(request.user, "change", Relationship, pk)

    if request.method == "POST":
        form = RelationshipForm(request.POST, instance=relationship)
        attach_creator_field(form, request.user, relationship)
        if form.is_valid():
            form.save()
            apply_creator_field(form, request.user, relationship)
            messages.success(request, "Relationship updated successfully!")
            return redirect("relationship_detail", pk=relationship.pk)
    else:
        form = RelationshipForm(instance=relationship)
        attach_creator_field(form, request.user, relationship)

    return render(
        request,
        "relationships/relationship_form.html",
        {"form": form, "relationship": relationship},
    )


@login_required
def relationship_delete_view(request, pk):
    relationship = get_permitted_object(request.user, "delete", Relationship, pk)

    if request.method == "POST":
        relationship.delete()
        messages.success(request, "Relationship deleted successfully!")
        return redirect("relationship_list")

    return render(request, "relationships/relationship_confirm_delete.html", {"relationship": relationship})


def _get_visible_queryset(model_class, user):
    permitted = get_permitted_objects(user, "view", model_class)
    permitted_ids = [obj.id for obj in permitted]
    return model_class.objects.filter(id__in=permitted_ids)


def _get_from_people_queryset(user):
    if user.has_perm("relationships.delegate_relationship"):
        return _get_visible_queryset(User, user)
    return User.objects.filter(id=user.id)


def _get_from_org_queryset(model_class, user):
    visible = _get_visible_queryset(model_class, user)
    return visible.filter(models.Q(owners=user) | models.Q(admins=user)).distinct()


@login_required
def relationship_proposal_create_view(request):
    from_people = _get_from_people_queryset(request.user)
    from_communities = _get_from_org_queryset(Community, request.user)
    from_projects = _get_from_org_queryset(Project, request.user)
    to_people = _get_visible_queryset(User, request.user)
    to_communities = _get_visible_queryset(Community, request.user)
    to_projects = _get_visible_queryset(Project, request.user)

    if request.method == "POST":
        form = RelationshipProposalForm(
            request.POST,
            from_people=from_people,
            from_communities=from_communities,
            from_projects=from_projects,
            to_people=to_people,
            to_communities=to_communities,
            to_projects=to_projects,
        )
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.initiator = request.user
            if proposal.from_person_id and proposal.from_person_id != request.user.id:
                if not request.user.has_perm("relationships.delegate_relationship"):
                    form.add_error(
                        "from_person",
                        "You do not have permission to propose on behalf of this person.",
                    )
                    return render(
                        request,
                        "relationships/relationship_proposal_form.html",
                        {"form": form},
                    )
            if proposal.from_community_id:
                if not (
                    proposal.from_community.owners.filter(id=request.user.id).exists()
                    or proposal.from_community.admins.filter(id=request.user.id).exists()
                ):
                    form.add_error(
                        "from_community",
                        "You do not have permission to propose on behalf of this organization.",
                    )
                    return render(
                        request,
                        "relationships/relationship_proposal_form.html",
                        {"form": form},
                    )
            if proposal.from_project_id:
                if not (
                    proposal.from_project.owners.filter(id=request.user.id).exists()
                    or proposal.from_project.admins.filter(id=request.user.id).exists()
                ):
                    form.add_error(
                        "from_project",
                        "You do not have permission to propose on behalf of this project.",
                    )
                    return render(
                        request,
                        "relationships/relationship_proposal_form.html",
                        {"form": form},
                    )
            if proposal.to_community_id:
                if not (
                    proposal.to_community.owners.exists()
                    or proposal.to_community.admins.exists()
                ):
                    form.add_error(
                        "to_community",
                        "Selected organization has no owners or admins set.",
                    )
                    return render(
                        request,
                        "relationships/relationship_proposal_form.html",
                        {"form": form},
                    )
            if proposal.to_project_id:
                if not (
                    proposal.to_project.owners.exists()
                    or proposal.to_project.admins.exists()
                ):
                    form.add_error(
                        "to_project",
                        "Selected project has no owners or admins set.",
                    )
                    return render(
                        request,
                        "relationships/relationship_proposal_form.html",
                        {"form": form},
                    )
            proposal.save()
            messages.success(request, "Relationship proposal sent.")
            return redirect("relationship_proposal_detail", proposal.id)
    else:
        form = RelationshipProposalForm(
            from_people=from_people,
            from_communities=from_communities,
            from_projects=from_projects,
            to_people=to_people,
            to_communities=to_communities,
            to_projects=to_projects,
        )

    return render(
        request,
        "relationships/relationship_proposal_form.html",
        {"form": form},
    )


@login_required
def relationship_proposal_detail_view(request, pk):
    proposal = (
        RelationshipProposal.objects.select_related(
            "initiator",
            "from_person",
            "from_community",
            "from_project",
            "to_person",
            "to_community",
            "to_project",
            "relationship_type",
            "resolution",
            "counter_parent",
        )
        .prefetch_related("responses")
        .filter(pk=pk)
        .first()
    )
    if not proposal:
        raise PermissionDenied
    if not proposal.can_view(request.user):
        raise PermissionDenied

    can_respond = (
        proposal.status == RelationshipProposal.Status.PENDING
        and proposal.is_recipient(request.user)
    )
    response_form = RelationshipProposalResponseForm()

    if request.method == "POST":
        if not can_respond:
            raise PermissionDenied
        response_form = RelationshipProposalResponseForm(request.POST)
        if response_form.is_valid():
            action = request.POST.get("response_action")
            if action not in [
                RelationshipProposalResponse.Action.ACCEPTED,
                RelationshipProposalResponse.Action.DECLINED,
                RelationshipProposalResponse.Action.COUNTERED,
            ]:
                messages.error(request, "Invalid response action.")
            else:
                note = response_form.cleaned_data.get("note")
                if action == RelationshipProposalResponse.Action.ACCEPTED:
                    proposal.status = RelationshipProposal.Status.ACCEPTED
                    proposal.save(update_fields=["status", "updated_at"])
                    RelationshipInstance.objects.create(
                        relationship_type=proposal.relationship_type,
                        resolution=proposal.resolution,
                        initiator=proposal.initiator,
                        from_person=proposal.from_person,
                        from_community=proposal.from_community,
                        from_project=proposal.from_project,
                        to_person=proposal.to_person,
                        to_community=proposal.to_community,
                        to_project=proposal.to_project,
                        created_by=request.user,
                    )
                    RelationshipProposalResponse.objects.create(
                        proposal=proposal,
                        responder=request.user,
                        action=action,
                        note=note,
                    )
                    messages.success(request, "Relationship accepted.")
                    return redirect("relationship_proposal_detail", proposal.id)

                if action == RelationshipProposalResponse.Action.DECLINED:
                    proposal.status = RelationshipProposal.Status.DECLINED
                    proposal.save(update_fields=["status", "updated_at"])
                    RelationshipProposalResponse.objects.create(
                        proposal=proposal,
                        responder=request.user,
                        action=action,
                        note=note,
                    )
                    messages.success(request, "Relationship declined.")
                    return redirect("relationship_proposal_detail", proposal.id)

                if action == RelationshipProposalResponse.Action.COUNTERED:
                    resolution = response_form.cleaned_data.get("resolution")

                    if not resolution:
                        response_form.add_error(
                            "resolution",
                            "Provide a new resolution for the counter-proposal.",
                        )
                    else:
                        counter = RelationshipProposal.objects.create(
                            initiator=request.user,
                            from_person=proposal.to_person,
                            from_community=proposal.to_community,
                            from_project=proposal.to_project,
                            to_person=proposal.from_person,
                            to_community=proposal.from_community,
                            to_project=proposal.from_project,
                            relationship_type=proposal.relationship_type,
                            note=note,
                            resolution=resolution,
                            status=RelationshipProposal.Status.PENDING,
                            counter_parent=proposal,
                        )
                        proposal.status = RelationshipProposal.Status.COUNTERED
                        proposal.save(update_fields=["status", "updated_at"])
                        RelationshipProposalResponse.objects.create(
                            proposal=proposal,
                            responder=request.user,
                            action=action,
                            note=note,
                            counter_proposal=counter,
                        )
                        messages.success(request, "Counter-proposal sent.")
                        return redirect("relationship_proposal_detail", counter.id)

    return render(
        request,
        "relationships/relationship_proposal_detail.html",
        {"proposal": proposal, "can_respond": can_respond, "response_form": response_form},
    )
