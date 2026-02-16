from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.acl.utils import get_permitted_objects, get_permitted_object, is_permitted
from .models import Location, LocationCapital
from .forms import LocationForm
from django.core.exceptions import PermissionDenied
from apps.utils.pagination import paginate_queryset
from apps.utils.form_tokens import get_form_token, validate_form_token


def location_list_view(request):
    locations = get_permitted_objects(request.user, "view", Location)

    locations_page, pagination_data = paginate_queryset(locations, request, per_page=10)

    return render(request, "locations/location_list.html", {
        "locations": locations_page,
        "pagination": pagination_data,
    })


def location_detail_view(request, pk):
    location = get_permitted_object(request.user, "view", Location, pk)
    location_capitals = LocationCapital.objects.filter(location=location).select_related("capital")

    return render(request, "locations/location_detail.html", {
        "location": location,
        "location_capitals": location_capitals,
    })


@login_required
def location_create_view(request):
    if not is_permitted(request.user, "add", "locations.location"):
        raise PermissionDenied

    if request.method == "POST":
        if not validate_form_token(request, 'location_create'):
            messages.error(request, "This form has already been submitted. Please don't use the back button after submitting.")
            form = LocationForm()
            form_token = get_form_token(request, 'location_create')
            return render(request, "locations/location_form.html", {"form": form, "form_token": form_token})
        
        form = LocationForm(request.POST, request.FILES)
        if form.is_valid():
            location = form.save(commit=False)
            location.created_by = request.user
            form.save()
            messages.success(request, "Location created successfully!")
            return redirect("location_detail", pk=location.pk)
    else:
        form = LocationForm()

    form_token = get_form_token(request, 'location_create')
    return render(
        request,
        "locations/location_form.html",
        {"form": form, "form_token": form_token},
    )


@login_required
def location_edit_view(request, pk):
    location = get_permitted_object(request.user, "change", Location, pk)

    if request.method == "POST":
        form = LocationForm(request.POST, request.FILES, instance=location)
        if form.is_valid():
            form.save()
            messages.success(request, "Location updated successfully!")
            return redirect("location_detail", pk=location.pk)
    else:
        form = LocationForm(instance=location)

    return render(
        request,
        "locations/location_form.html",
        {"form": form, "location": location},
    )


@login_required
def location_delete_view(request, pk):
    location = get_permitted_object(request.user, "delete", Location, pk)

    if request.method == "POST":
        location.delete()
        messages.success(request, "Location deleted successfully!")
        return redirect("location_list")

    return render(
        request, "locations/location_confirm_delete.html", {"location": location}
    )
