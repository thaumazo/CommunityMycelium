from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.acl.utils import get_permitted_objects, get_permitted_object, is_permitted
from .models import Hat
from .forms import HatForm
from django.core.exceptions import PermissionDenied
from apps.utils.dump import dump


@login_required
def hat_list_view(request):
    hats = get_permitted_objects(request.user, "view", Hat)
    return render(request, "hats/hat_list.html", {"hats": hats})


@login_required
def hat_detail_view(request, pk):
    hat = get_permitted_object(request.user, "view", Hat, pk)
    return render(request, "hats/hat_detail.html", {"hat": hat})


@login_required
def hat_create_view(request):
    if not is_permitted(request.user, "add", "hats.hat"):
        raise PermissionDenied

    if request.method == "POST":
        form = HatForm(request.POST)
        if form.is_valid():
            hat = form.save(commit=False)
            hat.created_by = request.user
            hat.save()
            form.save_m2m()  # This line saves the agreements
            messages.success(request, "Hat created successfully!")
            return redirect("hat_list")
    else:
        form = HatForm()

    return render(
        request,
        "hats/hat_form.html",
        {"form": form},
    )


@login_required
def hat_edit_view(request, pk):
    hat = get_permitted_object(request.user, "change", Hat, pk)

    if request.method == "POST":
        form = HatForm(request.POST, instance=hat)
        if form.is_valid():
            form.save()
            messages.success(request, "Hat updated successfully!")
            return redirect("hat_detail", pk=hat.pk)
    else:
        form = HatForm(instance=hat)

    return render(
        request,
        "hats/hat_form.html",
        {"form": form, "hat": hat},
    )


@login_required
def hat_delete_view(request, pk):
    hat = get_permitted_object(request.user, "delete", Hat, pk)

    if request.method == "POST":
        hat.delete()
        messages.success(request, "Hat deleted successfully!")
        return redirect("hat_list")

    return render(request, "hats/hat_confirm_delete.html", {"hat": hat})
