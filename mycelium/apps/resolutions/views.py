from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.acl.utils import get_permitted_objects, get_permitted_object, is_permitted
from .models import Resolution
from .forms import ResolutionForm
from django.core.exceptions import PermissionDenied
from apps.utils.dump import dump
from apps.utils.pagination import paginate_queryset


@login_required
def resolution_list_view(request):
    resolutions = get_permitted_objects(request.user, "view", Resolution)
    
    # Pagination using helper function
    resolutions_page, pagination_data = paginate_queryset(resolutions, request, per_page=10)
    
    return render(request, "resolutions/resolution_list.html", {
        "resolutions": resolutions_page,
        "pagination": pagination_data,
    })


@login_required
def resolution_detail_view(request, pk):
    resolution = get_permitted_object(request.user, "view", Resolution, pk)
    return render(request, "resolutions/resolution_detail.html", {"resolution": resolution})


@login_required
def resolution_create_view(request):
    if not is_permitted(request.user, "add", "resolutions.resolution"):
        raise PermissionDenied

    if request.method == "POST":
        form = ResolutionForm(request.POST)
        if form.is_valid():
            resolution = form.save(commit=False)
            resolution.created_by = request.user
            resolution.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, "Resolution created successfully!")
            return redirect("resolution_list")
    else:
        form = ResolutionForm()

    return render(
        request,
        "resolutions/resolution_form.html",
        {"form": form},
    )


@login_required
def resolution_edit_view(request, pk):
    resolution = get_permitted_object(request.user, "change", Resolution, pk)

    if request.method == "POST":
        form = ResolutionForm(request.POST, instance=resolution)
        if form.is_valid():
            form.save()
            messages.success(request, "Resolution updated successfully!")
            return redirect("resolution_detail", pk=resolution.pk)
    else:
        form = ResolutionForm(instance=resolution)

    return render(
        request,
        "resolutions/resolution_form.html",
        {"form": form, "resolution": resolution},
    )


@login_required
def resolution_delete_view(request, pk):
    resolution = get_permitted_object(request.user, "delete", Resolution, pk)

    if request.method == "POST":
        resolution.delete()
        messages.success(request, "Resolution deleted successfully!")
        return redirect("resolution_list")

    return render(
        request, "resolutions/resolution_confirm_delete.html", {"resolution": resolution}
    )
