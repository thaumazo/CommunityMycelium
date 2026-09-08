from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.utils import timezone

from apps.acl.utils import get_permitted_objects, get_permitted_object, is_permitted
from apps.utils.pagination import paginate_queryset
from apps.utils.form_tokens import get_form_token, validate_form_token

from .models import Commons, CommonsApplication, CommonsInvite
from .forms import CommonsForm, CommonsApplicationForm, CommonsInviteForm


def _is_commons_admin(user, commons):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user in commons.owners.all() or user in commons.admins.all()


@login_required
def commons_list_view(request):
    commons_qs = get_permitted_objects(request.user, "view", Commons)
    commons_list = list(commons_qs)

    my_commons_ids = set(request.user.owned_commons.values_list("pk", flat=True)) \
        | set(request.user.admin_commons.values_list("pk", flat=True)) \
        | set(request.user.member_commons.values_list("pk", flat=True))
    my_commons = sorted(
        (c for c in commons_list if c.pk in my_commons_ids),
        key=lambda c: c.title.lower(),
    )
    other_commons = [c for c in commons_list if c.pk not in my_commons_ids]

    commons_page, pagination_data = paginate_queryset(other_commons, request, per_page=10)

    return render(request, "commons/commons_list.html", {
        "commons_list": commons_page,
        "my_commons": my_commons,
        "pagination": pagination_data,
    })


@login_required
def commons_detail_view(request, pk):
    commons = get_permitted_object(request.user, "view", Commons, pk)

    is_member = request.user in commons.members.all()
    is_admin = _is_commons_admin(request.user, commons)
    pending_application = CommonsApplication.objects.filter(
        commons=commons, applicant=request.user, status=CommonsApplication.STATUS_PENDING
    ).first()
    pending_invite = CommonsInvite.objects.filter(
        commons=commons, invited_user=request.user, status=CommonsInvite.STATUS_PENDING
    ).first()

    can_apply = (
        request.user.is_authenticated
        and not is_member
        and not is_admin
        and not pending_application
        and not pending_invite
    )

    applications = commons.applications.filter(status=CommonsApplication.STATUS_PENDING) if is_admin else []
    invites = commons.invites.filter(status=CommonsInvite.STATUS_PENDING) if is_admin else []

    return render(request, "commons/commons_detail.html", {
        "commons": commons,
        "is_member": is_member,
        "is_admin": is_admin,
        "can_apply": can_apply,
        "pending_application": pending_application,
        "pending_invite": pending_invite,
        "applications": applications,
        "invites": invites,
        "invite_form": CommonsInviteForm(commons=commons) if is_admin else None,
    })


@login_required
def commons_create_view(request):
    if not is_permitted(request.user, "add", "commons.commons"):
        raise PermissionDenied

    if request.method == "POST":
        if not validate_form_token(request, "commons_create"):
            messages.error(request, "This form has already been submitted. Please don't use the back button after submitting.")
            form = CommonsForm(current_user=request.user)
            form_token = get_form_token(request, "commons_create")
            return render(request, "commons/commons_form.html", {"form": form, "form_token": form_token})

        form = CommonsForm(request.POST, current_user=request.user)
        if form.is_valid():
            commons = form.save(commit=False)
            commons.created_by = request.user
            commons.save()
            form.save_m2m()
            commons.owners.add(request.user)
            messages.success(request, "Commons created successfully!")
            return redirect("commons_detail", pk=commons.pk)
    else:
        form = CommonsForm(current_user=request.user)

    form_token = get_form_token(request, "commons_create")
    return render(request, "commons/commons_form.html", {"form": form, "form_token": form_token})


@login_required
def commons_edit_view(request, pk):
    commons = get_permitted_object(request.user, "change", Commons, pk)

    if request.method == "POST":
        form = CommonsForm(request.POST, instance=commons, current_user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Commons updated successfully!")
            return redirect("commons_detail", pk=commons.pk)
    else:
        form = CommonsForm(instance=commons, current_user=request.user)

    return render(request, "commons/commons_form.html", {"form": form, "commons": commons})


@login_required
def commons_delete_view(request, pk):
    commons = get_permitted_object(request.user, "delete", Commons, pk)

    if request.method == "POST":
        commons.delete()
        messages.success(request, "Commons deleted successfully!")
        return redirect("commons_list")

    return render(request, "commons/commons_confirm_delete.html", {"commons": commons})


@login_required
def commons_apply_view(request, pk):
    commons = get_permitted_object(request.user, "view", Commons, pk)

    if request.user in commons.members.all() or _is_commons_admin(request.user, commons):
        messages.info(request, "You're already part of this commons.")
        return redirect("commons_detail", pk=commons.pk)

    if CommonsApplication.objects.filter(
        commons=commons, applicant=request.user, status=CommonsApplication.STATUS_PENDING
    ).exists():
        messages.info(request, "You already have a pending application to this commons.")
        return redirect("commons_detail", pk=commons.pk)

    if request.method == "POST":
        form = CommonsApplicationForm(request.POST)
        if form.is_valid():
            CommonsApplication.objects.create(
                commons=commons,
                applicant=request.user,
                note=form.cleaned_data.get("note", ""),
            )
            messages.success(request, "Application submitted. A commons owner or admin will review it.")
            return redirect("commons_detail", pk=commons.pk)
    else:
        form = CommonsApplicationForm()

    return render(request, "commons/commons_apply_form.html", {"form": form, "commons": commons})


@login_required
def commons_application_respond_view(request, pk, application_pk):
    commons = get_permitted_object(request.user, "view", Commons, pk)
    if not _is_commons_admin(request.user, commons):
        raise PermissionDenied

    application = get_object_or_404(
        CommonsApplication, pk=application_pk, commons=commons, status=CommonsApplication.STATUS_PENDING
    )

    if request.method == "POST":
        decision = request.POST.get("decision")
        if decision not in ("approve", "decline"):
            raise Http404
        application.status = (
            CommonsApplication.STATUS_APPROVED if decision == "approve" else CommonsApplication.STATUS_DECLINED
        )
        application.decided_by = request.user
        application.decided_at = timezone.now()
        application.save()
        if decision == "approve":
            commons.members.add(application.applicant)
            messages.success(request, f"{application.applicant} approved as a member.")
        else:
            messages.info(request, f"Application from {application.applicant} declined.")

    return redirect("commons_detail", pk=commons.pk)


@login_required
def commons_invite_create_view(request, pk):
    commons = get_permitted_object(request.user, "view", Commons, pk)
    if not _is_commons_admin(request.user, commons):
        raise PermissionDenied

    if request.method == "POST":
        form = CommonsInviteForm(request.POST, commons=commons)
        if form.is_valid():
            invited_user = form.cleaned_data["invited_user"]
            invite, created = CommonsInvite.objects.get_or_create(
                commons=commons,
                invited_user=invited_user,
                status=CommonsInvite.STATUS_PENDING,
                defaults={"invited_by": request.user},
            )
            if created:
                messages.success(request, f"Invite sent to {invited_user}.")
            else:
                messages.info(request, f"{invited_user} already has a pending invite.")
        else:
            messages.error(request, "Please choose a valid person to invite.")

    return redirect("commons_detail", pk=commons.pk)


@login_required
def commons_invite_respond_view(request, pk, invite_pk):
    commons = get_permitted_object(request.user, "view", Commons, pk)
    invite = get_object_or_404(
        CommonsInvite, pk=invite_pk, commons=commons, invited_user=request.user,
        status=CommonsInvite.STATUS_PENDING,
    )

    if request.method == "POST":
        decision = request.POST.get("decision")
        if decision not in ("accept", "decline"):
            raise Http404
        invite.status = CommonsInvite.STATUS_ACCEPTED if decision == "accept" else CommonsInvite.STATUS_DECLINED
        invite.decided_at = timezone.now()
        invite.save()
        if decision == "accept":
            commons.members.add(request.user)
            messages.success(request, f"You've joined {commons.title}.")
        else:
            messages.info(request, f"You declined the invite to {commons.title}.")

    return redirect("commons_detail", pk=commons.pk)
