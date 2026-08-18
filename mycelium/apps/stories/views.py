from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.db.models import Q
from apps.acl.utils import get_permitted_objects, get_permitted_object, is_permitted
from apps.utils.pagination import paginate_queryset
from apps.utils.form_tokens import get_form_token, validate_form_token
from apps.utils.superuser_fields import attach_creator_field, apply_creator_field
from .models import Story, StoryMedia, StoryAttachment, StoryGeoPin, StoryLink
from .forms import StoryForm, StoryMediaForm


def _attachment_type_config():
    from apps.bioregions.models import Bioregion
    from apps.projects.models import Project
    from apps.users.models import User
    from apps.communities.models import Community
    from apps.challenges.models import Challenge
    from apps.capitals.models import Capital
    from apps.metacrisis_facets.models import Metacrisis_facet
    from apps.locations.models import Location

    return {
        "bioregion": {
            "app_label": "bioregions",
            "model_name": "bioregion",
            "model": Bioregion,
            "label": "Bioregion",
            "display": lambda obj: obj.title,
            "search": ["title", "description"],
        },
        "project": {
            "app_label": "projects",
            "model_name": "project",
            "model": Project,
            "label": "Project",
            "display": lambda obj: obj.title,
            "search": ["title", "description"],
        },
        "person": {
            "app_label": "users",
            "model_name": "user",
            "model": User,
            "label": "Person",
            "display": lambda obj: obj.get_full_name() or obj.username,
            "search": ["full_name", "username", "email"],
        },
        "community": {
            "app_label": "communities",
            "model_name": "community",
            "model": Community,
            "label": "Community",
            "display": lambda obj: obj.title,
            "search": ["title", "description"],
        },
        "challenge": {
            "app_label": "challenges",
            "model_name": "challenge",
            "model": Challenge,
            "label": "Challenge",
            "display": lambda obj: obj.title,
            "search": ["title", "description"],
        },
        "capital": {
            "app_label": "capitals",
            "model_name": "capital",
            "model": Capital,
            "label": "Permaculture Capital",
            "display": lambda obj: obj.title,
            "search": ["title", "description"],
        },
        "metacrisis_facet": {
            "app_label": "metacrisis_facets",
            "model_name": "metacrisis_facet",
            "model": Metacrisis_facet,
            "label": "Metacrisis Facet",
            "display": lambda obj: obj.title,
            "search": ["title", "description"],
        },
        "location": {
            "app_label": "locations",
            "model_name": "location",
            "model": Location,
            "label": "Location",
            "display": lambda obj: obj.title,
            "search": ["title", "description", "address"],
        },
    }


def _connection_for_object(obj):
    for config in _attachment_type_config().values():
        if isinstance(obj, config["model"]):
            return {
                "token": f"{config['app_label']}.{config['model_name']}:{obj.pk}",
                "label": config["display"](obj),
                "typeLabel": config["label"],
            }
    return None


def _bioregions_for_context_object(obj):
    if hasattr(obj, "bioregions"):
        return list(obj.bioregions.all())
    if hasattr(obj, "user_bioregions"):
        return list(obj.user_bioregions.all())
    return []


def _derive_connection_defaults_and_recommendations(attachment_target, user):
    defaults = []
    recommendations = []
    seen = set()

    def add_item(container, item_obj, reason=""):
        if not item_obj or not is_permitted(user, "view", item_obj):
            return
        item = _connection_for_object(item_obj)
        if not item:
            return
        if item["token"] in seen:
            return
        seen.add(item["token"])
        if reason:
            item["reason"] = reason
        container.append(item)

    from apps.projects.models import ProjectCapitalIn, ProjectCapitalOut

    if isinstance(attachment_target, (ProjectCapitalIn, ProjectCapitalOut)):
        add_item(defaults, attachment_target.project, "Source context")
        add_item(defaults, attachment_target.capital, "Source context")
        for bioregion in attachment_target.project.bioregions.all():
            add_item(recommendations, bioregion, "Connected bioregion from project")
        return defaults, recommendations

    add_item(defaults, attachment_target, "Source context")
    for bioregion in _bioregions_for_context_object(attachment_target):
        add_item(recommendations, bioregion, "Connected bioregion")

    return defaults, recommendations


@login_required
def story_attachment_options_view(request):
    type_key = (request.GET.get("type") or "").strip()
    query = (request.GET.get("q") or "").strip()
    config = _attachment_type_config().get(type_key)
    if not config:
        return JsonResponse({"results": []})

    permitted = get_permitted_objects(request.user, "view", config["model"])
    queryset = permitted if hasattr(permitted, "filter") else config["model"].objects.filter(
        pk__in=[obj.pk for obj in permitted]
    )

    if query:
        search_q = Q()
        for field in config["search"]:
            search_q |= Q(**{f"{field}__icontains": query})
        queryset = queryset.filter(search_q)

    queryset = queryset.order_by("pk")[:25]

    results = []
    for obj in queryset:
        token = f"{config['app_label']}.{config['model_name']}:{obj.pk}"
        results.append({
            "id": obj.pk,
            "token": token,
            "label": config["display"](obj),
            "typeLabel": config["label"],
        })

    return JsonResponse({"results": results})


def _parse_attachment_targets(raw_text):
    parsed = []
    if not raw_text:
        return parsed

    for line in raw_text.splitlines():
        item = line.strip()
        if not item:
            continue
        if ':' not in item or '.' not in item.split(':', 1)[0]:
            raise ValidationError(f"Invalid attachment target format: {item}")

        type_part, object_id_part = item.split(':', 1)
        app_label, model_name = type_part.split('.', 1)

        try:
            object_id = int(object_id_part.strip())
        except ValueError:
            raise ValidationError(f"Invalid attachment object id in: {item}")

        parsed.append((app_label.strip(), model_name.strip(), object_id))

    return parsed


def _parse_geo_pins(raw_text):
    pins = []
    if not raw_text:
        return pins

    for line in raw_text.splitlines():
        item = line.strip()
        if not item:
            continue

        parts = [p.strip() for p in item.split(',')]
        if len(parts) < 2:
            raise ValidationError(f"Invalid geo pin format: {item}")

        try:
            latitude = float(parts[0])
            longitude = float(parts[1])
        except ValueError:
            raise ValidationError(f"Invalid geo pin coordinates: {item}")

        label = parts[2] if len(parts) >= 3 else ""
        radius_m = None
        if len(parts) >= 4 and parts[3] != "":
            try:
                radius_m = float(parts[3])
            except ValueError:
                raise ValidationError(f"Invalid geo pin radius in: {item}")

        pins.append({
            "latitude": latitude,
            "longitude": longitude,
            "label": label,
            "radius_m": radius_m,
        })

    return pins


def _parse_linked_story_ids(raw_text):
    ids = []
    if not raw_text:
        return ids

    for token in raw_text.split(','):
        value = token.strip()
        if not value:
            continue
        try:
            ids.append(int(value))
        except ValueError:
            raise ValidationError(f"Invalid linked story id: {value}")

    return ids


def _sync_story_contexts(story, cleaned_data, user):
    attachment_targets = _parse_attachment_targets(cleaned_data.get("attachment_targets", ""))
    geo_pins = _parse_geo_pins(cleaned_data.get("geo_pins_input", ""))
    linked_story_ids = _parse_linked_story_ids(cleaned_data.get("linked_story_ids", ""))
    link_relation = cleaned_data.get("story_link_relation") or StoryLink.RELATION_CONTINUATION

    StoryAttachment.objects.filter(story=story).delete()
    for app_label, model_name, object_id in attachment_targets:
        if not StoryAttachment.is_attachable_content_type(app_label, model_name):
            raise ValidationError(f"Attachments to {app_label}.{model_name} are not allowed.")

        content_type = ContentType.objects.get(app_label=app_label, model=model_name)
        model_class = content_type.model_class()
        if not model_class:
            raise ValidationError(f"Unknown attachment target model: {app_label}.{model_name}")

        content_object = model_class.objects.filter(pk=object_id).first()
        if not content_object:
            raise ValidationError(f"Attachment target not found: {app_label}.{model_name}:{object_id}")
        if not is_permitted(user, "view", content_object):
            raise PermissionDenied(f"No permission to attach story to {app_label}.{model_name}:{object_id}")

        StoryAttachment.objects.create(
            story=story,
            content_type=content_type,
            object_id=object_id,
        )

    StoryGeoPin.objects.filter(story=story).delete()
    for pin in geo_pins:
        StoryGeoPin.objects.create(
            story=story,
            latitude=pin["latitude"],
            longitude=pin["longitude"],
            label=pin["label"],
            radius_m=pin["radius_m"],
        )

    StoryLink.objects.filter(from_story=story).delete()
    for target_id in linked_story_ids:
        if target_id == story.pk:
            continue
        target_story = Story.objects.filter(pk=target_id).first()
        if not target_story:
            raise ValidationError(f"Linked story not found: {target_id}")
        if not is_permitted(user, "view", target_story):
            raise PermissionDenied(f"No permission to link to story {target_id}")

        StoryLink.objects.create(
            from_story=story,
            to_story=target_story,
            relation_type=link_relation,
            created_by=user,
        )


def story_list_view(request):
    """View a list of all stories the user has access to."""
    stories = get_permitted_objects(request.user, "view", Story)
    if hasattr(stories, "prefetch_related"):
        stories = stories.prefetch_related("attachments__content_type", "attachments__content_object")

    attached_to = (request.GET.get("attached_to") or "").strip()
    attached_to_label = ""
    if attached_to:
        try:
            model_part, object_id_part = attached_to.split(":", 1)
            app_label, model_name = model_part.split(".", 1)
            object_id = int(object_id_part)

            if StoryAttachment.is_attachable_content_type(app_label, model_name):
                content_type = ContentType.objects.get(app_label=app_label, model=model_name)
                attachment_story_ids = StoryAttachment.objects.filter(
                    content_type=content_type,
                    object_id=object_id,
                ).values_list("story_id", flat=True)
                attachment_story_id_set = set(attachment_story_ids)
                if hasattr(stories, "filter"):
                    stories = stories.filter(pk__in=attachment_story_id_set)
                else:
                    stories = [s for s in stories if s.pk in attachment_story_id_set]

                model_class = content_type.model_class()
                if model_class:
                    target_obj = model_class.objects.filter(pk=object_id).first()
                    if target_obj:
                        attached_to_label = str(target_obj)
        except Exception:
            # Ignore malformed filters and fall back to unfiltered list.
            pass
    
    # Pagination
    stories_page, pagination_data = paginate_queryset(stories, request, per_page=20)
    
    return render(request, "stories/story_list.html", {
        "stories": stories_page,
        "pagination": pagination_data,
        "attached_to": attached_to,
        "attached_to_label": attached_to_label,
    })


def story_detail_view(request, pk):
    """View a story's details."""
    story = get_permitted_object(request.user, "view", Story, pk)
    try:
        story = Story.objects.prefetch_related("attachments__content_type", "attachments__content_object").get(pk=story.pk)
    except Story.DoesNotExist:
        pass
    
    # Capture the 'next' parameter for contextual back navigation
    # Fall back to HTTP referer if no 'next' parameter
    back_url = request.GET.get('next')
    if not back_url:
        back_url = request.META.get('HTTP_REFERER')
    
    # If we still don't have a back URL, default to story list
    if not back_url:
        from django.urls import reverse
        back_url = reverse('story_list')
    
    return render(request, "stories/story_detail.html", {
        "story": story,
        "back_url": back_url,
    })


@login_required
def story_create_view(request):
    """Create a new story."""
    # Authenticated users can always create stories (the question is whether they can attach them)

    def can_submit_project_community_note(user, target):
        from apps.projects.models import ProjectCapitalIn, ProjectCapitalOut

        if not user.is_authenticated:
            return False
        if not isinstance(target, (ProjectCapitalIn, ProjectCapitalOut)):
            return False

        project = target.project
        if not is_permitted(user, "view", project):
            return False

        return True
    
    # Check if we're attaching to a specific object
    attach_to_type = request.GET.get('attach_to_type')
    attach_to_id = request.GET.get('attach_to_id')
    is_community_note_submission = (request.GET.get("community_note") or "").strip().lower() in {"1", "true", "yes", "on"}
    community_note_type = (request.GET.get("note_type") or "").strip().lower()
    is_valid_note_type = community_note_type in {Story.NOTE_TYPE_IDEA, Story.NOTE_TYPE_OFFER}
    
    # If attaching to an object, verify the user has permission to change that object
    attachment_target = None
    default_connections = []
    recommended_connections = []
    if attach_to_type and attach_to_id:
        try:
            app_label, model_name = attach_to_type.split('.')
            content_type = ContentType.objects.get(
                app_label=app_label,
                model=model_name
            )
            model_class = content_type.model_class()
            attachment_target = model_class.objects.get(pk=attach_to_id)

            # Check if user has permission to change the attachment target
            has_change_permission = is_permitted(request.user, "change", attachment_target)
            can_submit_community_note = (
                is_community_note_submission
                and is_valid_note_type
                and can_submit_project_community_note(request.user, attachment_target)
            )

            if not has_change_permission and not can_submit_community_note:
                messages.error(request, "You don't have permission to attach stories to this object.")
                raise PermissionDenied

            default_connections, recommended_connections = _derive_connection_defaults_and_recommendations(
                attachment_target,
                request.user,
            )
        except ValueError as e:
            messages.error(request, f"Invalid attachment type format: {e}")
            raise PermissionDenied
        except ContentType.DoesNotExist as e:
            messages.error(request, f"Attachment target not found: {e}")
            raise PermissionDenied
        except PermissionDenied:
            # Re-raise permission denied without wrapping
            raise
        except Exception as e:
            if "does not exist" in str(e).lower():
                messages.error(request, f"Attachment target not found: {e}")
                raise PermissionDenied
            # Log unexpected errors but don't expose details to user
            print(f"Unexpected error in story_create_view: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            messages.error(request, "An error occurred while processing the attachment target.")
            raise PermissionDenied
    
    if request.method == "POST":
        if not validate_form_token(request, 'story_create'):
            messages.error(request, "This form has already been submitted. Please don't use the back button after submitting.")
            form = StoryForm()
            form_token = get_form_token(request, 'story_create')
            context = {
                "form": form,
                "attach_to_type": attach_to_type,
                "attach_to_id": attach_to_id,
                "default_connections": default_connections,
                "recommended_connections": recommended_connections,
                "is_community_note_submission": is_community_note_submission and is_valid_note_type,
                "community_note_type": community_note_type,
                "form_token": form_token,
            }
            return render(request, "stories/story_form.html", context)
        
        form = StoryForm(request.POST)
        if form.is_valid():
            story = form.save(commit=False)
            story.created_by = request.user

            if attachment_target and is_community_note_submission and is_valid_note_type and can_submit_project_community_note(request.user, attachment_target):
                story.is_community_note = True
                story.community_note_type = community_note_type
                story.community_note_status = Story.COMMUNITY_NOTE_PENDING
                story.view_members = False
                story.view_public = False

            story.save()

            try:
                _sync_story_contexts(story, form.cleaned_data, request.user)
            except (ValidationError, PermissionDenied) as exc:
                story.delete()
                messages.error(request, f"Story context could not be saved: {exc}")
                form_token = get_form_token(request, 'story_create')
                context = {
                    "form": form,
                    "attach_to_type": attach_to_type,
                    "attach_to_id": attach_to_id,
                    "default_connections": default_connections,
                    "recommended_connections": recommended_connections,
                    "is_community_note_submission": is_community_note_submission and is_valid_note_type,
                    "community_note_type": community_note_type,
                    "form_token": form_token,
                }
                return render(request, "stories/story_form.html", context)

            if story.is_community_note:
                messages.success(request, "Community note submitted successfully!")
                return redirect("project_detail", pk=attachment_target.project.pk)

            messages.success(request, "Story created successfully!")
            return redirect("story_detail", pk=story.pk)
    else:
        form = StoryForm()

        if default_connections:
            initial_tokens = "\n".join([item["token"] for item in default_connections])
            form.fields["attachment_targets"].initial = initial_tokens
    
    form_token = get_form_token(request, 'story_create')
    context = {
        "form": form,
        "attach_to_type": attach_to_type,
        "attach_to_id": attach_to_id,
        "default_connections": default_connections,
        "recommended_connections": recommended_connections,
        "is_community_note_submission": is_community_note_submission and is_valid_note_type,
        "community_note_type": community_note_type,
        "form_token": form_token,
    }
    
    return render(request, "stories/story_form.html", context)


@login_required
def story_edit_view(request, pk):
    """Edit a story."""
    story = get_permitted_object(request.user, "change", Story, pk)
    
    if request.method == "POST":
        form = StoryForm(request.POST, instance=story)
        attach_creator_field(form, request.user, story)
        if form.is_valid():
            updated_story = form.save()
            apply_creator_field(form, request.user, updated_story)
            try:
                _sync_story_contexts(updated_story, form.cleaned_data, request.user)
            except (ValidationError, PermissionDenied) as exc:
                messages.error(request, f"Story context could not be saved: {exc}")
                return render(request, "stories/story_form.html", {
                    "form": form,
                    "story": story,
                    "default_connections": [],
                    "recommended_connections": [],
                })
            messages.success(request, "Story updated successfully!")
            return redirect("story_detail", pk=story.pk)
    else:
        form = StoryForm(instance=story)
        attach_creator_field(form, request.user, story)
    
    return render(request, "stories/story_form.html", {
        "form": form,
        "story": story,
        "default_connections": [],
        "recommended_connections": [],
    })


@login_required
def story_delete_view(request, pk):
    """Delete a story."""
    story = get_permitted_object(request.user, "delete", Story, pk)
    
    if request.method == "POST":
        story.delete()
        messages.success(request, "Story deleted successfully!")
        return redirect("story_list")
    
    return render(request, "stories/story_confirm_delete.html", {"story": story})


@login_required
def story_add_media_view(request, story_pk):
    """Add media to a story."""
    story = get_permitted_object(request.user, "change", Story, story_pk)
    
    if request.method == "POST":
        form = StoryMediaForm(request.POST, request.FILES)
        if form.is_valid():
            media = form.save(commit=False)
            media.story = story
            media.save()
            messages.success(request, "Media added successfully!")
            return redirect("story_detail", pk=story.pk)
    else:
        form = StoryMediaForm()
    
    return render(request, "stories/story_media_form.html", {
        "form": form,
        "story": story,
    })


@login_required
def story_delete_media_view(request, media_pk):
    """Delete media from a story."""
    media = get_object_or_404(StoryMedia, pk=media_pk)
    story = get_permitted_object(request.user, "change", Story, media.story.pk)
    
    if request.method == "POST":
        media.delete()
        messages.success(request, "Media deleted successfully!")
        return redirect("story_detail", pk=story.pk)
    
    return render(request, "stories/story_media_confirm_delete.html", {
        "media": media,
        "story": story,
    })
