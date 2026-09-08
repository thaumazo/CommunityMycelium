from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from apps.acl.utils import get_permitted_objects, get_permitted_object, is_permitted
from apps.bookmarks.models import Bookmark
from .models import Community
from .forms import CommunityForm
from django.core.exceptions import PermissionDenied
from apps.utils.dump import dump
from apps.utils.pagination import paginate_queryset
from apps.utils.form_tokens import get_form_token, validate_form_token
from apps.utils.superuser_fields import attach_creator_field, apply_creator_field


@login_required
def community_list_view(request):
    communities = get_permitted_objects(request.user, "view", Community)
    
    # Float bookmarked communities to the top
    community_content_type = ContentType.objects.get_for_model(Community)
    bookmarked_ids = set(
        Bookmark.objects.filter(
            user=request.user,
            content_type=community_content_type
        ).values_list('object_id', flat=True)
    )
    # Separate bookmarked from non-bookmarked
    communities_list = list(communities)
    bookmarked_communities = [c for c in communities_list if c.pk in bookmarked_ids]
    non_bookmarked_communities = [c for c in communities_list if c.pk not in bookmarked_ids]
    communities_list = bookmarked_communities + non_bookmarked_communities
    
    # Pagination using helper function
    communities_page, pagination_data = paginate_queryset(communities_list, request, per_page=10)
    
    return render(
        request, "communities/community_list.html", {
            "communities": communities_page,
            "pagination": pagination_data,
        }
    )


@login_required
def community_detail_view(request, pk):
    from apps.stories.models import Story, StoryAttachment
    from apps.locations.models import Location

    community = get_permitted_object(request.user, "view", Community, pk)

    permitted_locations = get_permitted_objects(request.user, "view", Location)
    community_location_ids = community.locations.values_list("pk", flat=True)
    if hasattr(permitted_locations, "filter"):
        community_locations = permitted_locations.filter(pk__in=community_location_ids).order_by("title")
        community_location_count = community_locations.count()
    else:
        permitted_location_ids = {loc.pk for loc in permitted_locations}
        community_locations = list(community.locations.filter(pk__in=permitted_location_ids).order_by("title"))
        community_location_count = len(community_locations)

    community_content_type = ContentType.objects.get_for_model(Community)
    attached_story_ids = set(
        StoryAttachment.objects.filter(
            content_type=community_content_type,
            object_id=community.pk,
        ).values_list("story_id", flat=True)
    )

    permitted_stories = get_permitted_objects(request.user, "view", Story)
    if hasattr(permitted_stories, "filter"):
        community_stories = permitted_stories.filter(pk__in=attached_story_ids).order_by("-created_at")
        community_story_count = community_stories.count()
        community_stories_preview = community_stories[:3]
    else:
        community_stories = [s for s in permitted_stories if s.pk in attached_story_ids]
        community_stories.sort(key=lambda s: s.created_at, reverse=True)
        community_story_count = len(community_stories)
        community_stories_preview = community_stories[:3]

    return render(
        request,
        "communities/community_detail.html",
        {
            "community": community,
            "community_story_count": community_story_count,
            "community_stories_preview": community_stories_preview,
            "community_locations": community_locations,
            "community_location_count": community_location_count,
        },
    )


@login_required
def community_create_view(request):
    if not is_permitted(request.user, "add", "communities.community"):
        raise PermissionDenied

    if request.method == "POST":
        if not validate_form_token(request, 'community_create'):
            messages.error(request, "This form has already been submitted. Please don't use the back button after submitting.")
            form = CommunityForm(current_user=request.user)
            form_token = get_form_token(request, 'community_create')
            return render(request, "communities/community_form.html", {"form": form, "form_token": form_token})
        
        form = CommunityForm(request.POST, request.FILES, current_user=request.user)
        if form.is_valid():
            community = form.save(commit=False)
            community.created_by = request.user
            community.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, "Community created successfully!")
            return redirect("community_detail", pk=community.pk)
    else:
        form = CommunityForm(current_user=request.user)

    form_token = get_form_token(request, 'community_create')
    return render(
        request,
        "communities/community_form.html",
        {"form": form, "form_token": form_token},
    )


@login_required
def community_edit_view(request, pk):
    community = get_permitted_object(request.user, "change", Community, pk)

    if request.method == "POST":
        form = CommunityForm(request.POST, request.FILES, instance=community, current_user=request.user)
        attach_creator_field(form, request.user, community)
        if form.is_valid():
            form.save()
            apply_creator_field(form, request.user, community)
            messages.success(request, "Community updated successfully!")
            return redirect("community_detail", pk=community.pk)
    else:
        form = CommunityForm(instance=community, current_user=request.user)
        attach_creator_field(form, request.user, community)

    return render(
        request,
        "communities/community_form.html",
        {"form": form, "community": community},
    )


@login_required
def community_delete_view(request, pk):
    community = get_permitted_object(request.user, "delete", Community, pk)

    if request.method == "POST":
        community.delete()
        messages.success(request, "Community deleted successfully!")
        return redirect("community_list")

    return render(
        request, "communities/community_confirm_delete.html", {"community": community}
    )
