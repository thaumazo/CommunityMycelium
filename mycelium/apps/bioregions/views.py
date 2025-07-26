from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.acl.utils import get_permitted_objects, get_permitted_object, is_permitted
from .models import Bioregion
from .forms import BioregionForm
from django.core.exceptions import PermissionDenied
from apps.utils.dump import dump
from apps.utils.pagination import paginate_queryset


@login_required
def bioregion_list_view(request):
    bioregions = get_permitted_objects(request.user, "view", Bioregion)
    
    # Pagination using helper function
    bioregions_page, pagination_data = paginate_queryset(bioregions, request, per_page=10)
    
    return render(request, "bioregions/bioregion_list.html", {
        "bioregions": bioregions_page,
        "pagination": pagination_data,
    })


@login_required
def bioregion_detail_view(request, pk):
    bioregion = get_permitted_object(request.user, "view", Bioregion, pk)
    return render(request, "bioregions/bioregion_detail.html", {"bioregion": bioregion})


@login_required
def bioregion_create_view(request):
    if not is_permitted(request.user, "add", "bioregions.bioregion"):
        raise PermissionDenied

    if request.method == "POST":
        form = BioregionForm(request.POST)
        if form.is_valid():
            bioregion = form.save(commit=False)
            bioregion.created_by = request.user
            bioregion.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, "Bioregion created successfully!")
            return redirect("bioregion_list")
    else:
        form = BioregionForm()

    return render(
        request,
        "bioregions/bioregion_form.html",
        {"form": form},
    )


@login_required
def bioregion_edit_view(request, pk):
    bioregion = get_permitted_object(request.user, "change", Bioregion, pk)

    if request.method == "POST":
        form = BioregionForm(request.POST, instance=bioregion)
        if form.is_valid():
            form.save()
            messages.success(request, "Bioregion updated successfully!")
            return redirect("bioregion_detail", pk=bioregion.pk)
    else:
        form = BioregionForm(instance=bioregion)

    return render(
        request,
        "bioregions/bioregion_form.html",
        {"form": form, "bioregion": bioregion},
    )


@login_required
def bioregion_delete_view(request, pk):
    bioregion = get_permitted_object(request.user, "delete", Bioregion, pk)

    if request.method == "POST":
        bioregion.delete()
        messages.success(request, "Bioregion deleted successfully!")
        return redirect("bioregion_list")

    return render(request, "bioregions/bioregion_confirm_delete.html", {"bioregion": bioregion})
