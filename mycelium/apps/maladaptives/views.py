from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.acl.utils import get_permitted_objects, get_permitted_object, is_permitted
from .models import Maladaptive
from .forms import MaladaptiveForm
from django.core.exceptions import PermissionDenied
from apps.utils.dump import dump
from apps.utils.pagination import paginate_queryset


@login_required
def maladaptive_list_view(request):
    maladaptives = get_permitted_objects(request.user, "view", Maladaptive)
    
    # Pagination using helper function
    maladaptives_page, pagination_data = paginate_queryset(maladaptives, request, per_page=10)
    
    return render(request, "maladaptives/maladaptive_list.html", {
        "maladaptives": maladaptives_page,
        "pagination": pagination_data,
    })


@login_required
def maladaptive_detail_view(request, pk):
    maladaptive = get_permitted_object(request.user, "view", Maladaptive, pk)
    return render(request, "maladaptives/maladaptive_detail.html", {"maladaptive": maladaptive})


@login_required
def maladaptive_create_view(request):
    if not is_permitted(request.user, "add", "maladaptives.maladaptive"):
        raise PermissionDenied

    if request.method == "POST":
        form = MaladaptiveForm(request.POST)
        if form.is_valid():
            maladaptive = form.save(commit=False)
            maladaptive.created_by = request.user
            maladaptive.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, "Maladaptive Schema created successfully!")
            return redirect("maladaptive_list")
    else:
        form = MaladaptiveForm()

    return render(
        request,
        "maladaptives/maladaptive_form.html",
        {"form": form},
    )


@login_required
def maladaptive_edit_view(request, pk):
    maladaptive = get_permitted_object(request.user, "change", Maladaptive, pk)

    if request.method == "POST":
        form = MaladaptiveForm(request.POST, instance=maladaptive)
        if form.is_valid():
            form.save()
            messages.success(request, "Maladaptive Schema updated successfully!")
            return redirect("maladaptive_detail", pk=maladaptive.pk)
    else:
        form = MaladaptiveForm(instance=maladaptive)

    return render(
        request,
        "maladaptives/maladaptive_form.html",
        {"form": form, "maladaptive": maladaptive},
    )


@login_required
def maladaptive_delete_view(request, pk):
    maladaptive = get_permitted_object(request.user, "delete", Maladaptive, pk)

    if request.method == "POST":
        maladaptive.delete()
        messages.success(request, "Maladaptive Schema deleted successfully!")
        return redirect("maladaptive_list")

    return render(request, "maladaptives/maladaptive_confirm_delete.html", {"maladaptive": maladaptive})
