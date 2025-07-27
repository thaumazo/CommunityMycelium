from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.acl.utils import get_permitted_objects, get_permitted_object, is_permitted
from .models import Socialrole
from .forms import SocialroleForm
from django.core.exceptions import PermissionDenied
from apps.utils.dump import dump
from apps.utils.pagination import paginate_queryset


@login_required
def socialrole_list_view(request):
    socialroles = get_permitted_objects(request.user, "view", Socialrole)
    
    # Pagination using helper function
    socialroles_page, pagination_data = paginate_queryset(socialroles, request, per_page=10)
    
    return render(request, "socialroles/socialrole_list.html", {
        "socialroles": socialroles_page,
        "pagination": pagination_data,
    })


@login_required
def socialrole_detail_view(request, pk):
    socialrole = get_permitted_object(request.user, "view", Socialrole, pk)
    return render(request, "socialroles/socialrole_detail.html", {"socialrole": socialrole})


@login_required
def socialrole_create_view(request):
    if not is_permitted(request.user, "add", "socialroles.socialrole"):
        raise PermissionDenied

    if request.method == "POST":
        form = SocialroleForm(request.POST)
        if form.is_valid():
            socialrole = form.save(commit=False)
            socialrole.created_by = request.user
            socialrole.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, "Social Role created successfully!")
            return redirect("socialrole_list")
    else:
        form = SocialroleForm()

    return render(
        request,
        "socialroles/socialrole_form.html",
        {"form": form},
    )


@login_required
def socialrole_edit_view(request, pk):
    socialrole = get_permitted_object(request.user, "change", Socialrole, pk)

    if request.method == "POST":
        form = SocialroleForm(request.POST, instance=socialrole)
        if form.is_valid():
            form.save()
            messages.success(request, "Social Role updated successfully!")
            return redirect("socialrole_detail", pk=socialrole.pk)
    else:
        form = SocialroleForm(instance=socialrole)

    return render(
        request,
        "socialroles/socialrole_form.html",
        {"form": form, "socialrole": socialrole},
    )


@login_required
def socialrole_delete_view(request, pk):
    socialrole = get_permitted_object(request.user, "delete", Socialrole, pk)

    if request.method == "POST":
        socialrole.delete()
        messages.success(request, "Social Role deleted successfully!")
        return redirect("socialrole_list")

    return render(request, "socialroles/socialrole_confirm_delete.html", {"socialrole": socialrole})
