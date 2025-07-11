from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.acl.utils import get_permitted_objects, get_permitted_object, is_permitted
from .models import Community
from .forms import CommunityForm
from django.core.exceptions import PermissionDenied
from apps.utils.dump import dump
from apps.utils.pagination import paginate_queryset


@login_required
def community_list_view(request):
    communities = get_permitted_objects(request.user, "view", Community)
    
    # Pagination using helper function
    communities_page, pagination_data = paginate_queryset(communities, request, per_page=10)
    
    return render(
        request, "communities/community_list.html", {
            "communities": communities_page,
            "pagination": pagination_data,
        }
    )


@login_required
def community_detail_view(request, pk):
    community = get_permitted_object(request.user, "view", Community, pk)
    return render(
        request, "communities/community_detail.html", {"community": community}
    )


@login_required
def community_create_view(request):
    if not is_permitted(request.user, "add", "communities.community"):
        raise PermissionDenied

    if request.method == "POST":
        form = CommunityForm(request.POST)
        if form.is_valid():
            community = form.save(commit=False)
            community.created_by = request.user
            community.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, "Community created successfully!")
            return redirect("community_list")
    else:
        form = CommunityForm()

    return render(
        request,
        "communities/community_form.html",
        {"form": form},
    )


@login_required
def community_edit_view(request, pk):
    community = get_permitted_object(request.user, "change", Community, pk)

    if request.method == "POST":
        form = CommunityForm(request.POST, instance=community)
        if form.is_valid():
            form.save()
            messages.success(request, "Community updated successfully!")
            return redirect("community_detail", pk=community.pk)
    else:
        form = CommunityForm(instance=community)

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
