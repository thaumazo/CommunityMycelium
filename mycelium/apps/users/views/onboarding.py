from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from apps.bioregions.models import Bioregion
from apps.commons.models import Commons, CommonsApplication, CommonsInvite
from apps.acl.utils import get_permitted_objects
from apps.projects.models import Project
from ..forms import OnboardingForm
from ..models import BioregionRequest, OnboardingHomeLocation, User


SECTIONS = [
    ("place", "Place"),
    ("character", "Character Class"),
    ("metacrisis", "Metacrisis"),
    ("pitfalls", "Pitfalls"),
    ("commons", "Commons"),
    ("activity", "Activity"),
]
REQUIRED_SELECTIONS = {
    "character": "user_socialroles",
    "metacrisis": "user_metacrisis_facets",
}


def _orientation_project(user):
    return Project.objects.filter(orientation_user=user).first()


def _create_orientation_project(user, starter_choice="explore"):
    from apps.projects.models import Project, MoveStep

    choices_info = {
        "explore": (
            "Orientation Move: Explore the Network",
            "A starting Move where you favourite (bookmark) at least one person, one community, and one Move.",
            [
                (1, "Favourite at least one person", "Find a person in the directory and click the star icon to bookmark them."),
                (2, "Favourite at least one community", "Find a community that interests you and bookmark it."),
                (3, "Favourite at least one Move", "Explore active Moves in your region and bookmark one to follow."),
            ],
        ),
        "reflect": (
            "Orientation Move: Reflect & Share Stories",
            "A starting Move where you write at least three stories tagged to your Metacrisis facets, pitfalls, or social roles.",
            [
                (1, "Write a story tagged to a Metacrisis facet", "Share an observation, experience, or reflection about a Metacrisis facet."),
                (2, "Write a story tagged to a Social Role", "Share a story about your experience in a Social Role / Character Class."),
                (3, "Write a story tagged to a Pitfall", "Reflect on a personal or organizational pitfall you have encountered."),
            ],
        ),
        "connect": (
            "Orientation Move: Connect to a Commons",
            "A starting Move where you find a Commons operating in your area or focus and submit a request to join.",
            [
                (1, "Browse available Commons", "Explore Commons operating in your bioregion or focus area."),
                (2, "Submit a request to join a Commons", "Apply to join a Commons to collaborate with others."),
            ],
        ),
    }

    title, description, steps_data = choices_info.get(starter_choice, choices_info["explore"])

    project, created = Project.objects.get_or_create(
        orientation_user=user,
        defaults={
            "title": title,
            "description": description,
            "is_orientation": True,
            "created_by": user,
            "view_members": False,
            "view_public": False,
        },
    )
    if not created:
        project.title = title
        project.description = description
        project.save(update_fields=["title", "description"])
        # Clear existing orientation steps if starter choice was changed or steps are empty
        project.steps.all().delete()
    else:
        project.owners.add(user)
        project.members.add(user)

    for order, step_title, step_desc in steps_data:
        MoveStep.objects.create(
            project=project,
            order=order,
            title=step_title,
            description=step_desc,
        )

    return project


def _save_home_location(user, form):
    title = (form.cleaned_data.get("home_location_title") or "").strip()
    if not title:
        return
    location, _ = OnboardingHomeLocation.objects.update_or_create(
        user=user,
        defaults={
            "title": title,
            "description": form.cleaned_data.get("home_location_description") or "",
        },
    )
    return location


def _save_bioregion_request(user, form):
    title = (form.cleaned_data.get("requested_bioregion_title") or "").strip()
    if not title:
        return
    BioregionRequest.objects.create(
        requested_by=user,
        title=title,
        description=form.cleaned_data.get("requested_bioregion_description") or "",
    )


def _section_is_skipped(user, section):
    return section in (user.onboarding_skipped_sections or [])


def _next_section(section):
    section_keys = [key for key, _label in SECTIONS]
    try:
        return section_keys[section_keys.index(section) + 1]
    except (ValueError, IndexError):
        return section_keys[0]


@login_required
def onboarding_view(request):
    user = request.user
    if user.onboarding_status != User.ONBOARDING_IN_PROGRESS:
        return redirect("core:home")

    skipped_sections = list(user.onboarding_skipped_sections or [])
    completed_sections = list(user.onboarding_completed_sections or [])
    form = OnboardingForm(instance=user, current_user=user)
    action = ""
    section = ""
    starter_choice = "explore"

    if request.method == "POST":
        if "action_save" in request.POST:
            action = "save"
            section = request.POST.get("action_save", "").strip().lower()
        elif "action_skip" in request.POST:
            action = "skip"
            section = request.POST.get("action_skip", "").strip().lower()
        elif "action_finish" in request.POST:
            action = "finish"
            section = "activity"
            starter_choice = request.POST.get("action_finish", "explore").strip().lower()
            if starter_choice not in {"explore", "reflect", "connect"}:
                starter_choice = "explore"
        else:
            action = (request.POST.get("action") or "").strip().lower()
            section = (request.POST.get("section") or "").strip().lower()

        if section not in dict(SECTIONS):
            section = "place"

        form = OnboardingForm(request.POST, instance=user, current_user=user)
        if action == "skip":
            if section not in skipped_sections:
                skipped_sections.append(section)
            if section in completed_sections:
                completed_sections.remove(section)
            user.onboarding_skipped_sections = skipped_sections
            user.onboarding_completed_sections = completed_sections
            user.onboarding_step = _next_section(section)
            user.save(update_fields=["onboarding_skipped_sections", "onboarding_completed_sections", "onboarding_step"])
            messages.info(request, f"{dict(SECTIONS)[section]} marked as skipped. You can return to it whenever you like.")
            return redirect(f"{reverse('onboarding')}?section={_next_section(section)}")

        if action == "save":
            if not form.is_valid():
                messages.error(request, "Please correct the highlighted fields before continuing.")
            elif section in REQUIRED_SELECTIONS and not form.cleaned_data.get(REQUIRED_SELECTIONS[section]).exists():
                messages.error(request, f"Choose at least one {dict(SECTIONS)[section]} or use Skip for now.")
            else:
                with transaction.atomic():
                    onboarding_user = form.save(commit=False)
                    onboarding_user.save()
                    form.save_m2m()
                    _save_home_location(user, form)
                    _save_bioregion_request(user, form)
                    selected_commons = form.cleaned_data.get("visible_to_commons")
                    if selected_commons is not None:
                        user.visible_to_commons.set(selected_commons)
                    if section in skipped_sections:
                        skipped_sections.remove(section)
                    if section not in completed_sections:
                        completed_sections.append(section)
                    user.onboarding_skipped_sections = skipped_sections
                    user.onboarding_completed_sections = completed_sections
                    user.onboarding_step = _next_section(section)
                    user.save(update_fields=["onboarding_skipped_sections", "onboarding_completed_sections", "onboarding_step"])
                messages.success(request, f"{dict(SECTIONS)[section]} saved.")
                return redirect(f"{reverse('onboarding')}?section={_next_section(section)}")

        if action == "finish":
            if not form.is_valid():
                messages.error(request, "Please correct the highlighted fields before completing orientation.")
            else:
                missing = [
                    label for key, label in (("character", "Character Class"), ("metacrisis", "Metacrisis"))
                    if key not in skipped_sections
                    and not form.cleaned_data.get(REQUIRED_SELECTIONS[key]).exists()
                ]
                if missing:
                    messages.error(request, f"Choose at least one option in: {', '.join(missing)}, or skip those sections.")
                else:
                    with transaction.atomic():
                        onboarding_user = form.save(commit=False)
                        onboarding_user.save()
                        form.save_m2m()
                        _save_home_location(user, form)
                        _save_bioregion_request(user, form)
                        selected_commons = form.cleaned_data.get("visible_to_commons")
                        if selected_commons is not None:
                            user.visible_to_commons.set(selected_commons)
                        orientation_move = _create_orientation_project(user, starter_choice=starter_choice)
                        user.onboarding_status = User.ONBOARDING_COMPLETED
                        user.onboarding_completed_at = timezone.now()
                        user.onboarding_step = "completed"
                        user.onboarding_completed_sections = list(dict(SECTIONS).keys())
                        user.save(update_fields=["onboarding_status", "onboarding_completed_at", "onboarding_step", "onboarding_completed_sections"])
                    messages.success(request, f"Orientation complete! Your starter Move ('{orientation_move.title}') has been added to your dashboard.")
                    return redirect("core:home")

    invited_commons = CommonsInvite.objects.filter(
        invited_user=user, status=CommonsInvite.STATUS_PENDING
    ).select_related("commons", "invited_by")
    requested_commons = CommonsApplication.objects.filter(
        applicant=user, status=CommonsApplication.STATUS_PENDING
    ).select_related("commons")
    orientation_move = _orientation_project(user)
    selected_bioregions = user.user_bioregions.all()
    if form.is_bound and form.is_valid():
        selected_bioregions = form.cleaned_data.get("user_bioregions") or selected_bioregions
    available_commons = get_permitted_objects(user, "view", Commons)
    if hasattr(available_commons, "filter") and selected_bioregions.exists():
        available_commons = available_commons.filter(bioregion__in=selected_bioregions).distinct()

    requested_section = (request.GET.get("section") or "").strip().lower()
    current_section = requested_section if requested_section in dict(SECTIONS) else user.onboarding_step
    if current_section not in dict(SECTIONS):
        current_section = "place"

    return render(request, "users/onboarding.html", {
        "form": form,
        "sections": SECTIONS,
        "skipped_sections": skipped_sections,
        "completed_sections": completed_sections,
        "current_section": current_section,
        "invited_commons": invited_commons,
        "requested_commons": requested_commons,
        "orientation_move": orientation_move,
        "available_commons": available_commons,
    })


@login_required
def onboarding_complete_view(request):
    orientation_move = get_object_or_404(Project, orientation_user=request.user)
    return render(request, "users/onboarding_complete.html", {"orientation_move": orientation_move})
