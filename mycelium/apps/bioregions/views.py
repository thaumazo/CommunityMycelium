from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.acl.utils import get_permitted_objects, get_permitted_object, is_permitted
from .models import Bioregion
from .forms import BioregionForm
from django.core.exceptions import PermissionDenied
from apps.utils.dump import dump
from apps.utils.pagination import paginate_queryset
from apps.utils.form_tokens import get_form_token, validate_form_token


def bioregion_list_view(request):
    if request.user.is_authenticated:
        bioregions = get_permitted_objects(request.user, "view", Bioregion)
    else:
        # Anonymous users can see all bioregions (title/description only in template)
        bioregions = Bioregion.objects.all()
    
    # Pagination using helper function
    bioregions_page, pagination_data = paginate_queryset(bioregions, request, per_page=10)
    
    return render(request, "bioregions/bioregion_list.html", {
        "bioregions": bioregions_page,
        "pagination": pagination_data,
    })


def bioregion_detail_view(request, pk):
    if request.user.is_authenticated:
        bioregion = get_permitted_object(request.user, "view", Bioregion, pk)
    else:
        # Anonymous users can see bioregion title/description
        try:
            bioregion = Bioregion.objects.get(pk=pk)
        except Bioregion.DoesNotExist:
            from django.http import Http404
            raise Http404
    
    # Get communities connected to this bioregion
    from apps.communities.models import Community
    from apps.locations.models import Location
    if request.user.is_authenticated:
        from apps.acl.utils import get_permitted_objects
        all_communities = get_permitted_objects(request.user, "view", Community)
        # Filter to only communities connected to this bioregion
        communities = [c for c in all_communities if bioregion in c.bioregions.all()]
        all_locations = get_permitted_objects(request.user, "view", Location)
        locations = [l for l in all_locations if bioregion in l.bioregions.all()]
    else:
        communities = Community.objects.filter(bioregions=bioregion)
        locations = Location.objects.filter(bioregions=bioregion, view_public=True)
    
    return render(request, "bioregions/bioregion_detail.html", {
        "bioregion": bioregion,
        "communities": communities,
        "locations": locations,
    })


@login_required
def bioregion_create_view(request):
    if not is_permitted(request.user, "add", "bioregions.bioregion"):
        raise PermissionDenied

    if request.method == "POST":
        if not validate_form_token(request, 'bioregion_create'):
            messages.error(request, "This form has already been submitted. Please don't use the back button after submitting.")
            form = BioregionForm()
            form_token = get_form_token(request, 'bioregion_create')
            return render(request, "bioregions/bioregion_form.html", {"form": form, "form_token": form_token})
        
        form = BioregionForm(request.POST, request.FILES)
        if form.is_valid():
            bioregion = form.save(commit=False)
            bioregion.created_by = request.user
            bioregion.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, "Bioregion created successfully!")
            return redirect("bioregion_detail", pk=bioregion.pk)
    else:
        form = BioregionForm()

    form_token = get_form_token(request, 'bioregion_create')
    return render(
        request,
        "bioregions/bioregion_form.html",
        {"form": form, "form_token": form_token},
    )


@login_required
def bioregion_edit_view(request, pk):
    bioregion = get_permitted_object(request.user, "change", Bioregion, pk)

    if request.method == "POST":
        form = BioregionForm(request.POST, request.FILES, instance=bioregion)
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
