from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.contenttypes.models import ContentType
from apps.acl.utils import get_permitted_objects, get_permitted_object, is_permitted
from apps.utils.pagination import paginate_queryset
from .models import Story, StoryMedia, StoryAttachment
from .forms import StoryForm, StoryMediaForm


@login_required
def story_list_view(request):
    """View a list of all stories the user has access to."""
    stories = get_permitted_objects(request.user, "view", Story)
    
    # Pagination
    stories_page, pagination_data = paginate_queryset(stories, request, per_page=20)
    
    return render(request, "stories/story_list.html", {
        "stories": stories_page,
        "pagination": pagination_data,
    })


@login_required
def story_detail_view(request, pk):
    """View a story's details."""
    story = get_permitted_object(request.user, "view", Story, pk)
    return render(request, "stories/story_detail.html", {"story": story})


@login_required
def story_create_view(request):
    """Create a new story."""
    if not is_permitted(request.user, "add", "stories.story"):
        raise PermissionDenied
    
    # Check if we're attaching to a specific object
    attach_to_type = request.GET.get('attach_to_type')
    attach_to_id = request.GET.get('attach_to_id')
    
    if request.method == "POST":
        form = StoryForm(request.POST)
        if form.is_valid():
            story = form.save(commit=False)
            story.created_by = request.user
            story.save()
            
            # If attaching to a specific object, create the attachment
            if attach_to_type and attach_to_id:
                try:
                    app_label, model_name = attach_to_type.split('.')
                    content_type = ContentType.objects.get(
                        app_label=app_label,
                        model=model_name
                    )
                    StoryAttachment.objects.create(
                        story=story,
                        content_type=content_type,
                        object_id=attach_to_id
                    )
                except Exception as e:
                    print(f"Error creating attachment: {e}")
            
            messages.success(request, "Story created successfully!")
            return redirect("story_detail", pk=story.pk)
    else:
        form = StoryForm()
    
    context = {
        "form": form,
        "attach_to_type": attach_to_type,
        "attach_to_id": attach_to_id,
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
