from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.acl.utils import get_permitted_objects, get_permitted_object, is_permitted
from .models import Agreement
from .forms import AgreementForm
from django.core.exceptions import PermissionDenied
from apps.utils.dump import dump


@login_required
def agreement_list_view(request):
    agreements = get_permitted_objects(request.user, "view", Agreement)
    return render(request, "agreements/agreement_list.html", {"agreements": agreements})


@login_required
def agreement_detail_view(request, pk):
    agreement = get_permitted_object(request.user, "view", Agreement, pk)
    return render(request, "agreements/agreement_detail.html", {"agreement": agreement})


@login_required
def agreement_create_view(request):
    if not is_permitted(request.user, "add", "agreements.agreement"):
        raise PermissionDenied

    if request.method == "POST":
        form = AgreementForm(request.POST)
        if form.is_valid():
            agreement = form.save(commit=False)
            agreement.created_by = request.user
            agreement.save()
            messages.success(request, "Agreement created successfully!")
            return redirect("agreement_list")
    else:
        form = AgreementForm()

    return render(
        request,
        "agreements/agreement_form.html",
        {"form": form},
    )


@login_required
def agreement_edit_view(request, pk):
    agreement = get_permitted_object(request.user, "change", Agreement, pk)

    if request.method == "POST":
        form = AgreementForm(request.POST, instance=agreement)
        if form.is_valid():
            form.save()
            messages.success(request, "Agreement updated successfully!")
            return redirect("agreement_detail", pk=agreement.pk)
    else:
        form = AgreementForm(instance=agreement)

    return render(
        request,
        "agreements/agreement_form.html",
        {"form": form, "agreement": agreement},
    )


@login_required
def agreement_delete_view(request, pk):
    agreement = get_permitted_object(request.user, "delete", Agreement, pk)

    if request.method == "POST":
        agreement.delete()
        messages.success(request, "Agreement deleted successfully!")
        return redirect("agreement_list")

    return render(request, "agreements/agreement_confirm_delete.html", {"agreement": agreement})
