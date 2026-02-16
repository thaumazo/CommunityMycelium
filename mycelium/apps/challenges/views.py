from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.acl.utils import get_permitted_objects, get_permitted_object, is_permitted
from .models import Challenge
from .forms import ChallengeForm
from django.core.exceptions import PermissionDenied
from apps.utils.dump import dump
from apps.utils.pagination import paginate_queryset
from apps.utils.form_tokens import get_form_token, validate_form_token


@login_required
def challenge_list_view(request):
    challenges = get_permitted_objects(request.user, "view", Challenge)
    
    # Pagination using helper function
    challenges_page, pagination_data = paginate_queryset(challenges, request, per_page=128)
    
    return render(request, "challenges/challenge_list.html", {
        "challenges": challenges_page,
        "pagination": pagination_data,
    })


@login_required
def challenge_detail_view(request, pk):
    challenge = get_permitted_object(request.user, "view", Challenge, pk)
    return render(request, "challenges/challenge_detail.html", {"challenge": challenge})


@login_required
def challenge_create_view(request):
    if not is_permitted(request.user, "add", "challenges.challenge"):
        raise PermissionDenied

    if request.method == "POST":
        if not validate_form_token(request, 'challenge_create'):
            messages.error(request, "This form has already been submitted. Please don't use the back button after submitting.")
            form = ChallengeForm()
            form_token = get_form_token(request, 'challenge_create')
            return render(request, "challenges/challenge_form.html", {"form": form, "form_token": form_token})
        
        form = ChallengeForm(request.POST)
        if form.is_valid():
            challenge = form.save(commit=False)
            challenge.created_by = request.user
            challenge.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, "Challenge created successfully!")
            return redirect("challenge_detail", pk=challenge.pk)
    else:
        form = ChallengeForm()

    form_token = get_form_token(request, 'challenge_create')
    return render(
        request,
        "challenges/challenge_form.html",
        {"form": form, "form_token": form_token},
    )


@login_required
def challenge_edit_view(request, pk):
    challenge = get_permitted_object(request.user, "change", Challenge, pk)

    if request.method == "POST":
        form = ChallengeForm(request.POST, instance=challenge)
        if form.is_valid():
            form.save()
            messages.success(request, "Challenge updated successfully!")
            return redirect("challenge_detail", pk=challenge.pk)
    else:
        form = ChallengeForm(instance=challenge)

    return render(
        request,
        "challenges/challenge_form.html",
        {"form": form, "challenge": challenge},
    )


@login_required
def challenge_delete_view(request, pk):
    challenge = get_permitted_object(request.user, "delete", Challenge, pk)

    if request.method == "POST":
        challenge.delete()
        messages.success(request, "Challenge deleted successfully!")
        return redirect("challenge_list")

    return render(request, "challenges/challenge_confirm_delete.html", {"challenge": challenge})
