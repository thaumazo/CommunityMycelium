from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.contenttypes.models import ContentType
from apps.acl.utils import get_permitted_objects, get_permitted_object, is_permitted
from apps.utils.pagination import paginate_queryset
from apps.utils.form_tokens import get_form_token, validate_form_token
from .models import Story, StoryMedia, StoryAttachment
from .forms import StoryForm, StoryMediaForm


def story_list_view(request):
    """View a list of all stories the user has access to."""
    stories = get_permitted_objects(request.user, "view", Story)
    
    # Pagination
    stories_page, pagination_data = paginate_queryset(stories, request, per_page=20)
    
    return render(request, "stories/story_list.html", {
        "stories": stories_page,
        "pagination": pagination_data,
    })


def story_detail_view(request, pk):
    """View a story's details."""
    story = get_permitted_object(request.user, "view", Story, pk)
    
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
            
            # If attaching to a specific object, create the attachment
            if attachment_target:
                try:
                    content_type = ContentType.objects.get_for_model(attachment_target)
                    StoryAttachment.objects.create(
                        story=story,
                        content_type=content_type,
                        object_id=attachment_target.pk
                    )
                except Exception as e:
                    print(f"Error creating attachment: {e}")

            if story.is_community_note:
                messages.success(request, "Community note submitted successfully!")
                return redirect("project_detail", pk=attachment_target.project.pk)

            messages.success(request, "Story created successfully!")
            return redirect("story_detail", pk=story.pk)
    else:
        form = StoryForm()
    
    form_token = get_form_token(request, 'story_create')
    context = {
        "form": form,
        "attach_to_type": attach_to_type,
        "attach_to_id": attach_to_id,
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
        if form.is_valid():
            form.save()
            messages.success(request, "Story updated successfully!")
            return redirect("story_detail", pk=story.pk)
    else:
        form = StoryForm(instance=story)
    
    return render(request, "stories/story_form.html", {
        "form": form,
        "story": story,
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
