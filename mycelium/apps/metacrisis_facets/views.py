from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.acl.utils import get_permitted_objects, get_permitted_object, is_permitted
from .models import Metacrisis_facet
from .forms import Metacrisis_facetForm
from django.core.exceptions import PermissionDenied
from apps.utils.dump import dump
from apps.utils.pagination import paginate_queryset


@login_required
def metacrisis_facet_list_view(request):
    metacrisis_facets = get_permitted_objects(request.user, "view", Metacrisis_facet)
    
    # Pagination using helper function
    metacrisis_facets_page, pagination_data = paginate_queryset(metacrisis_facets, request, per_page=10)
    
    return render(request, "metacrisis_facets/metacrisis_facet_list.html", {
        "metacrisis_facets": metacrisis_facets_page,
        "pagination": pagination_data,
    })


@login_required
def metacrisis_facet_detail_view(request, pk):
    metacrisis_facet = get_permitted_object(request.user, "view", Metacrisis_facet, pk)
    return render(request, "metacrisis_facets/metacrisis_facet_detail.html", {"metacrisis_facet": metacrisis_facet})


@login_required
def metacrisis_facet_create_view(request):
    if not is_permitted(request.user, "add", "metacrisis_facets.metacrisis_facet"):
        raise PermissionDenied

    if request.method == "POST":
        form = Metacrisis_facetForm(request.POST)
        if form.is_valid():
            metacrisis_facet = form.save(commit=False)
            metacrisis_facet.created_by = request.user
            metacrisis_facet.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, "Metacrisis Facet created successfully!")
            return redirect("metacrisis_facet_list")
    else:
        form = Metacrisis_facetForm()

    return render(
        request,
        "metacrisis_facets/metacrisis_facet_form.html",
        {"form": form},
    )


@login_required
def metacrisis_facet_edit_view(request, pk):
    metacrisis_facet = get_permitted_object(request.user, "change", Metacrisis_facet, pk)

    if request.method == "POST":
        form = Metacrisis_facetForm(request.POST, instance=metacrisis_facet)
        if form.is_valid():
            form.save()
            messages.success(request, "Metacrisis Facet updated successfully!")
            return redirect("metacrisis_facet_detail", pk=metacrisis_facet.pk)
    else:
        form = Metacrisis_facetForm(instance=metacrisis_facet)

    return render(
        request,
        "metacrisis_facets/metacrisis_facet_form.html",
        {"form": form, "metacrisis_facet": metacrisis_facet},
    )


@login_required
def metacrisis_facet_delete_view(request, pk):
    metacrisis_facet = get_permitted_object(request.user, "delete", Metacrisis_facet, pk)

    if request.method == "POST":
        metacrisis_facet.delete()
        messages.success(request, "Metacrisis Facet deleted successfully!")
        return redirect("metacrisis_facet_list")

    return render(request, "metacrisis_facets/metacrisis_facet_confirm_delete.html", {"metacrisis_facet": metacrisis_facet})
