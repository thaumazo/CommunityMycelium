import json
import re
import unicodedata
from copy import deepcopy

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.acl.utils import get_permitted_objects, get_permitted_object, is_permitted
from .models import Project, ProjectCapitalIn, ProjectCapitalOut
from .forms import ProjectForm
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from apps.utils.dump import dump
from apps.utils.pagination import paginate_queryset
from apps.utils.form_tokens import get_form_token, validate_form_token


PROJECT_STORY_IMPORT_SCHEMA = {
    "schema_version": 1,
    "dry_run": False,
    "upsert_by_title": True,
    "create_missing_project_capital_links": False,
    "default_visibility": {
        "view_members": True,
        "view_public": False,
    },
    "stories": [
        {
            "title": "Learning to regenerate soil fertility",
            "text_content": "Narrative content for this project capital story.",
            "capital_direction": "in",
            "capital_title": "Natural Capital",
            "attachment_context": "regeneration_example",
            "youtube_url": "",
            "view_members": True,
            "view_public": False,
        },
        {
            "title": "Training loop outputs stronger facilitation",
            "text_content": "What this project produces as social capacity.",
            "capital_direction": "out",
            "capital_title": "Social Capital",
            "attachment_context": "capacity_output",
        },
    ],
}


def _normalize_capital_title(value):
    if value is None:
        return ""
    normalized = unicodedata.normalize("NFKC", str(value))
    normalized = normalized.replace("\u00A0", " ")
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip().lower()


def _normalize_story_title(value):
    return _normalize_capital_title(value)


def _apply_story_visibility(story, visibility_level):
    if visibility_level == "private":
        story.view_members = False
        story.view_public = False
    elif visibility_level == "members":
        story.view_members = True
        story.view_public = False
    elif visibility_level == "public":
        story.view_members = True
        story.view_public = True
    else:
        raise ValueError("Invalid visibility level. Use private, members, or public.")


def _project_story_queryset(project, scope="all"):
    from django.contrib.contenttypes.models import ContentType
    from apps.stories.models import Story

    ct_in = ContentType.objects.get_for_model(ProjectCapitalIn)
    ct_out = ContentType.objects.get_for_model(ProjectCapitalOut)

    in_ids = list(ProjectCapitalIn.objects.filter(project=project).values_list("id", flat=True))
    out_ids = list(ProjectCapitalOut.objects.filter(project=project).values_list("id", flat=True))

    in_filter = Q(attachments__content_type=ct_in, attachments__object_id__in=in_ids)
    out_filter = Q(attachments__content_type=ct_out, attachments__object_id__in=out_ids)

    if scope == "in":
        return Story.objects.filter(in_filter).distinct()
    if scope == "out":
        return Story.objects.filter(out_filter).distinct()
    return Story.objects.filter(in_filter | out_filter).distinct()


def _redirect_project_next_or_detail(project, safe_next):
    if safe_next:
        return redirect(safe_next)
    return redirect("project_detail", pk=project.pk)


def _project_story_import_schema_for(project):
    from apps.capitals.models import Capital

    project_capitals_in = sorted({
        pc.capital.title.strip()
        for pc in ProjectCapitalIn.objects.filter(project=project).select_related("capital")
    })
    project_capitals_out = sorted({
        pc.capital.title.strip()
        for pc in ProjectCapitalOut.objects.filter(project=project).select_related("capital")
    })
    all_capitals = sorted({
        capital.title.strip()
        for capital in Capital.objects.all()
    })

    schema = deepcopy(PROJECT_STORY_IMPORT_SCHEMA)
    schema["capital_title_reference"] = {
        "for_capital_direction_in_use_exactly": project_capitals_in,
        "for_capital_direction_out_use_exactly": project_capitals_out,
        "all_available_capitals_in_system": all_capitals,
    }
    schema["import_guidance"] = {
        "capital_title_matching": "Use exact titles from capital_title_reference. Matching is case-insensitive and whitespace-normalized.",
        "story_deduplication": "With upsert_by_title=true, importer updates existing story for same project capital + direction + title instead of creating duplicate.",
        "capital_direction_rules": {
            "in": "Story attaches to Project Capital In relationship for that capital title.",
            "out": "Story attaches to Project Capital Out relationship for that capital title.",
        },
        "create_missing_project_capital_links_behavior": (
            "When false, capital must already be linked to this project in the specified direction. "
            "When true, importer creates missing project-capital links if the capital title exists in system capitals."
        ),
    }
    return schema


def _normalize_story_import_payload(raw_payload):
    try:
        payload = json.loads(raw_payload)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {exc}")

    if not isinstance(payload, dict):
        raise ValueError("JSON root must be an object.")

    stories = payload.get("stories")
    if not isinstance(stories, list) or not stories:
        raise ValueError("'stories' must be a non-empty array.")

    default_visibility = payload.get("default_visibility", {})
    if not isinstance(default_visibility, dict):
        raise ValueError("'default_visibility' must be an object when provided.")

    default_view_members = bool(default_visibility.get("view_members", True))
    default_view_public = bool(default_visibility.get("view_public", False))

    normalized = []
    for index, story in enumerate(stories, start=1):
        if not isinstance(story, dict):
            raise ValueError(f"stories[{index}] must be an object.")

        title = (story.get("title") or "").strip()
        text_content = (story.get("text_content") or "").strip()
        capital_direction = (story.get("capital_direction") or "").strip().lower()
        capital_title = (story.get("capital_title") or "").strip()

        if not title:
            raise ValueError(f"stories[{index}].title is required.")
        if not text_content:
            raise ValueError(f"stories[{index}].text_content is required.")
        if capital_direction not in {"in", "out"}:
            raise ValueError(f"stories[{index}].capital_direction must be 'in' or 'out'.")
        if not capital_title:
            raise ValueError(f"stories[{index}].capital_title is required.")

        normalized.append({
            "title": title,
            "text_content": text_content,
            "capital_direction": capital_direction,
            "capital_title": capital_title,
            "attachment_context": (story.get("attachment_context") or "").strip(),
            "youtube_url": (story.get("youtube_url") or "").strip(),
            "view_members": bool(story.get("view_members", default_view_members)),
            "view_public": bool(story.get("view_public", default_view_public)),
        })

    return {
        "stories": normalized,
        "dry_run": bool(payload.get("dry_run", False)),
        "upsert_by_title": bool(payload.get("upsert_by_title", True)),
        "create_missing_project_capital_links": bool(payload.get("create_missing_project_capital_links", False)),
    }


def project_list_view(request):
    projects = get_permitted_objects(request.user, "view", Project)
    
    # Pagination using helper function
    projects_page, pagination_data = paginate_queryset(projects, request, per_page=10)
    
    return render(request, "projects/project_list.html", {
        "projects": projects_page,
        "pagination": pagination_data,
    })


def project_detail_view(request, pk):
    from apps.stories.models import Story, StoryAttachment
    from django.contrib.contenttypes.models import ContentType
    from django.db.models import Q
    
    project = get_permitted_object(request.user, "view", Project, pk)
    
    # Get through model instances for capitals
    project_capitals_in = ProjectCapitalIn.objects.filter(project=project).select_related('capital')
    project_capitals_out = ProjectCapitalOut.objects.filter(project=project).select_related('capital')
    
    # Get stories attached to project capital relationships
    story_attachments = {}
    
    # Check if current user is admin or owner of this project
    is_project_admin_or_owner = (
        request.user.is_authenticated and 
        (request.user in project.admins.all() or request.user in project.owners.all())
    )
    
    # Helper function to filter stories by visibility
    def get_visible_attachments(attachments):
        visible = []
        for attachment in attachments:
            story = attachment.story
            if request.user.is_authenticated:
                if (story.created_by == request.user or 
                    story.view_members or 
                    story.view_public or 
                    request.user.is_superuser or
                    is_project_admin_or_owner):  # Project admins/owners can see all stories
                    visible.append(attachment)
            else:
                if story.view_public:
                    visible.append(attachment)
        return visible
    
    # Get stories for capitals in (attached to ProjectCapitalIn instances)
    for project_capital in project_capitals_in:
        ct = ContentType.objects.get_for_model(project_capital)
        attachments = StoryAttachment.objects.filter(
            content_type=ct,
            object_id=project_capital.id
        ).select_related('story', 'story__created_by')
        
        visible_stories = get_visible_attachments(attachments)
        if visible_stories:
            # Key by capital_in id for template
            story_attachments[f'capital_in_{project_capital.capital.id}'] = visible_stories
    
    # Get stories for capitals out (attached to ProjectCapitalOut instances)
    for project_capital in project_capitals_out:
        ct = ContentType.objects.get_for_model(project_capital)
        attachments = StoryAttachment.objects.filter(
            content_type=ct,
            object_id=project_capital.id
        ).select_related('story', 'story__created_by')
        
        visible_stories = get_visible_attachments(attachments)
        if visible_stories:
            # Key by capital_out id for template
            story_attachments[f'capital_out_{project_capital.capital.id}'] = visible_stories
    
    return render(request, "projects/project_detail.html", {
        "project": project,
        "story_attachments": story_attachments,
        "project_capitals_in": project_capitals_in,
        "project_capitals_out": project_capitals_out,
        "story_import_schema": json.dumps(_project_story_import_schema_for(project), indent=2),
    })


@login_required
def project_story_import_view(request, pk):
    from django.contrib.contenttypes.models import ContentType
    from apps.capitals.models import Capital
    from apps.stories.models import Story, StoryAttachment

    project = get_permitted_object(request.user, "change", Project, pk)

    if request.method != "POST":
        return redirect("project_detail", pk=project.pk)

    raw_payload = (request.POST.get("story_import_json") or "").strip()
    if not raw_payload:
        messages.error(request, "Paste JSON into the import box before submitting.")
        return redirect("project_detail", pk=project.pk)

    try:
        payload = _normalize_story_import_payload(raw_payload)
    except ValueError as exc:
        messages.error(request, f"Import failed: {exc}")
        return redirect("project_detail", pk=project.pk)

    project_capitals_in = {
        _normalize_capital_title(pc.capital.title): pc
        for pc in ProjectCapitalIn.objects.filter(project=project).select_related("capital")
    }
    project_capitals_out = {
        _normalize_capital_title(pc.capital.title): pc
        for pc in ProjectCapitalOut.objects.filter(project=project).select_related("capital")
    }

    ct_in = ContentType.objects.get_for_model(ProjectCapitalIn)
    ct_out = ContentType.objects.get_for_model(ProjectCapitalOut)

    dry_run = (request.POST.get("dry_run") in {"1", "true", "on"}) or payload["dry_run"]
    upsert_by_title = payload["upsert_by_title"]
    created_count = 0
    updated_count = 0
    created_links_in = 0
    created_links_out = 0

    existing_story_targets = {}
    if upsert_by_title:
        in_relation_keys = {
            relation.pk: capital_key
            for capital_key, relation in project_capitals_in.items()
            if getattr(relation, "pk", None)
        }
        out_relation_keys = {
            relation.pk: capital_key
            for capital_key, relation in project_capitals_out.items()
            if getattr(relation, "pk", None)
        }

        if in_relation_keys:
            in_attachments = (
                StoryAttachment.objects.filter(content_type=ct_in, object_id__in=list(in_relation_keys.keys()))
                .select_related("story")
                .order_by("-story__updated_at", "-story__id", "-id")
            )
            for attachment in in_attachments:
                relation_key = in_relation_keys.get(attachment.object_id)
                if relation_key is None:
                    continue
                dedupe_key = ("in", relation_key, _normalize_story_title(attachment.story.title))
                if dedupe_key not in existing_story_targets:
                    existing_story_targets[dedupe_key] = attachment

        if out_relation_keys:
            out_attachments = (
                StoryAttachment.objects.filter(content_type=ct_out, object_id__in=list(out_relation_keys.keys()))
                .select_related("story")
                .order_by("-story__updated_at", "-story__id", "-id")
            )
            for attachment in out_attachments:
                relation_key = out_relation_keys.get(attachment.object_id)
                if relation_key is None:
                    continue
                dedupe_key = ("out", relation_key, _normalize_story_title(attachment.story.title))
                if dedupe_key not in existing_story_targets:
                    existing_story_targets[dedupe_key] = attachment

    try:
        with transaction.atomic():
            for story_data in payload["stories"]:
                capital_key = _normalize_capital_title(story_data["capital_title"])
                title_key = _normalize_story_title(story_data["title"])
                direction = story_data["capital_direction"]

                if direction == "in":
                    project_capital = project_capitals_in.get(capital_key)
                    if not project_capital and payload["create_missing_project_capital_links"]:
                        capital = Capital.objects.filter(title__iexact=story_data["capital_title"]).first()
                        if not capital:
                            raise ValueError(
                                f"Capital '{story_data['capital_title']}' does not exist. "
                                f"Create it first, or use an existing capital title."
                            )
                        if dry_run:
                            project_capital = ProjectCapitalIn(project=project, capital=capital)
                            created_links_in += 1
                        else:
                            project_capital, created = ProjectCapitalIn.objects.get_or_create(project=project, capital=capital)
                            if created:
                                created_links_in += 1
                        project_capitals_in[_normalize_capital_title(capital.title)] = project_capital

                    if not project_capital:
                        raise ValueError(
                            f"Project has no Capitals In link for '{story_data['capital_title']}'. "
                            f"Either add that capital to the project first or set create_missing_project_capital_links=true."
                        )

                    content_type = ct_in
                else:
                    project_capital = project_capitals_out.get(capital_key)
                    if not project_capital and payload["create_missing_project_capital_links"]:
                        capital = Capital.objects.filter(title__iexact=story_data["capital_title"]).first()
                        if not capital:
                            raise ValueError(
                                f"Capital '{story_data['capital_title']}' does not exist. "
                                f"Create it first, or use an existing capital title."
                            )
                        if dry_run:
                            project_capital = ProjectCapitalOut(project=project, capital=capital)
                            created_links_out += 1
                        else:
                            project_capital, created = ProjectCapitalOut.objects.get_or_create(project=project, capital=capital)
                            if created:
                                created_links_out += 1
                        project_capitals_out[_normalize_capital_title(capital.title)] = project_capital

                    if not project_capital:
                        raise ValueError(
                            f"Project has no Capitals Out link for '{story_data['capital_title']}'. "
                            f"Either add that capital to the project first or set create_missing_project_capital_links=true."
                        )

                    content_type = ct_out

                dedupe_key = (direction, capital_key, title_key)
                existing_attachment = existing_story_targets.get(dedupe_key) if upsert_by_title else None

                if existing_attachment:
                    if not dry_run:
                        story = existing_attachment.story
                        story.title = story_data["title"]
                        story.text_content = story_data["text_content"]
                        story.youtube_url = story_data["youtube_url"] or None
                        story.view_members = story_data["view_members"]
                        story.view_public = story_data["view_public"]
                        story.save()

                        existing_attachment.attachment_context = story_data["attachment_context"]
                        existing_attachment.save(update_fields=["attachment_context"])
                    updated_count += 1
                    continue

                if not dry_run:
                    story = Story.objects.create(
                        title=story_data["title"],
                        text_content=story_data["text_content"],
                        youtube_url=story_data["youtube_url"] or None,
                        created_by=request.user,
                        view_members=story_data["view_members"],
                        view_public=story_data["view_public"],
                    )

                    attachment = StoryAttachment.objects.create(
                        story=story,
                        content_type=content_type,
                        object_id=project_capital.pk,
                        attachment_context=story_data["attachment_context"],
                    )
                    if upsert_by_title:
                        existing_story_targets[dedupe_key] = attachment
                created_count += 1
    except ValueError as exc:
        messages.error(request, f"Import failed: {exc}")
        return redirect("project_detail", pk=project.pk)

    if dry_run:
        messages.success(
            request,
            f"Dry run successful: would create {created_count} stor{'y' if created_count == 1 else 'ies'} "
            f"and update {updated_count} existing stor{'y' if updated_count == 1 else 'ies'} "
            f"and create {created_links_in + created_links_out} missing project-capital link"
            f"{'s' if (created_links_in + created_links_out) != 1 else ''} "
            f"({created_links_in} in, {created_links_out} out). No data was written."
        )
    else:
        messages.success(
            request,
            f"Import successful: created {created_count} stor{'y' if created_count == 1 else 'ies'} "
            f"and updated {updated_count} existing stor{'y' if updated_count == 1 else 'ies'}."
        )
    return redirect("project_detail", pk=project.pk)


@login_required
def project_story_visibility_update_view(request, pk, story_pk):
    project = get_permitted_object(request.user, "change", Project, pk)
    if request.method != "POST":
        return redirect("project_detail", pk=project.pk)

    visibility_level = (request.POST.get("visibility_level") or "").strip().lower()
    next_url = (request.POST.get("next") or "").strip()
    safe_next = next_url if next_url.startswith("/") else ""

    story = _project_story_queryset(project).filter(pk=story_pk).first()
    if not story:
        messages.error(request, "Story not found on this project.")
        return _redirect_project_next_or_detail(project, safe_next)

    try:
        _apply_story_visibility(story, visibility_level)
    except ValueError as exc:
        messages.error(request, str(exc))
        return _redirect_project_next_or_detail(project, safe_next)

    story.save(update_fields=["view_members", "view_public", "updated_at"])
    messages.success(request, f"Updated visibility for '{story.title}'.")
    return _redirect_project_next_or_detail(project, safe_next)


@login_required
def project_story_visibility_bulk_update_view(request, pk):
    project = get_permitted_object(request.user, "change", Project, pk)
    if request.method != "POST":
        return redirect("project_detail", pk=project.pk)

    visibility_level = (request.POST.get("visibility_level") or "").strip().lower()
    scope = (request.POST.get("scope") or "all").strip().lower()
    selected_story_ids = request.POST.getlist("story_ids")
    next_url = (request.POST.get("next") or "").strip()
    safe_next = next_url if next_url.startswith("/") else ""

    if scope not in {"all", "in", "out"}:
        messages.error(request, "Invalid scope for bulk visibility update.")
        return _redirect_project_next_or_detail(project, safe_next)

    if not selected_story_ids:
        messages.error(request, "Select at least one story for bulk visibility update.")
        return _redirect_project_next_or_detail(project, safe_next)

    queryset = _project_story_queryset(project, scope=scope).filter(pk__in=selected_story_ids)

    updated_count = 0
    try:
        with transaction.atomic():
            for story in queryset:
                _apply_story_visibility(story, visibility_level)
                story.save(update_fields=["view_members", "view_public", "updated_at"])
                updated_count += 1
    except ValueError as exc:
        messages.error(request, str(exc))
        return _redirect_project_next_or_detail(project, safe_next)

    if updated_count == 0:
        messages.error(request, "No eligible stories found for update.")
    else:
        messages.success(request, f"Updated visibility for {updated_count} stor{'y' if updated_count == 1 else 'ies'}.")

    return _redirect_project_next_or_detail(project, safe_next)


@login_required
def project_create_view(request):
    if request.method == "POST":
        if not validate_form_token(request, 'project_create'):
            messages.error(request, "This form has already been submitted. Please don't use the back button after submitting.")
            form = ProjectForm()
            form_token = get_form_token(request, 'project_create')
            return render(request, "projects/project_form.html", {"form": form, "form_token": form_token})
        
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            form.save()  # This will save the project and m2m fields
            messages.success(request, "Project created successfully!")
            return redirect("project_detail", pk=project.pk)
    else:
        form = ProjectForm()

    form_token = get_form_token(request, 'project_create')
    return render(
        request,
        "projects/project_form.html",
        {"form": form, "form_token": form_token},
    )


@login_required
def project_edit_view(request, pk):
    project = get_permitted_object(request.user, "change", Project, pk)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Project updated successfully!")
            return redirect("project_detail", pk=project.pk)
    else:
        form = ProjectForm(instance=project)

    return render(
        request,
        "projects/project_form.html",
        {"form": form, "project": project},
    )


@login_required
def project_delete_view(request, pk):
    project = get_permitted_object(request.user, "delete", Project, pk)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Project deleted successfully!")
        return redirect("project_list")

    return render(request, "projects/project_confirm_delete.html", {"project": project})
