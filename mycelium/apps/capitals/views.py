from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.acl.utils import get_permitted_objects, get_permitted_object, is_permitted
from .models import Capital
from .forms import CapitalForm
from django.core.exceptions import PermissionDenied
from apps.utils.dump import dump
from apps.utils.pagination import paginate_queryset


@login_required
def capital_list_view(request):
    capitals = get_permitted_objects(request.user, "view", Capital)
    
    # Pagination using helper function
    capitals_page, pagination_data = paginate_queryset(capitals, request, per_page=10)
    
    return render(request, "capitals/capital_list.html", {
        "capitals": capitals_page,
        "pagination": pagination_data,
    })


@login_required
def capital_detail_view(request, pk):
    capital = get_permitted_object(request.user, "view", Capital, pk)
    return render(request, "capitals/capital_detail.html", {"capital": capital})


@login_required
def capital_create_view(request):
    if not is_permitted(request.user, "add", "capitals.capital"):
        raise PermissionDenied

    if request.method == "POST":
        form = CapitalForm(request.POST)
        if form.is_valid():
            capital = form.save(commit=False)
            capital.created_by = request.user
            capital.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, "Capital created successfully!")
            return redirect("capital_list")
    else:
        form = CapitalForm()

    return render(
        request,
        "capitals/capital_form.html",
        {"form": form},
    )


@login_required
def capital_edit_view(request, pk):
    capital = get_permitted_object(request.user, "change", Capital, pk)

    if request.method == "POST":
        form = CapitalForm(request.POST, instance=capital)
        if form.is_valid():
            form.save()
            messages.success(request, "Capital updated successfully!")
            return redirect("capital_detail", pk=capital.pk)
    else:
        form = CapitalForm(instance=capital)

    return render(
        request,
        "capitals/capital_form.html",
        {"form": form, "capital": capital},
    )


@login_required
def capital_delete_view(request, pk):
    capital = get_permitted_object(request.user, "delete", Capital, pk)

    if request.method == "POST":
        capital.delete()
        messages.success(request, "Capital deleted successfully!")
        return redirect("capital_list")

    return render(request, "capitals/capital_confirm_delete.html", {"capital": capital})
