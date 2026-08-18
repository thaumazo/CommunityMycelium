from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.acl.utils import get_permitted_objects, get_permitted_object, is_permitted
from .models import Meeting
from .forms import MeetingForm
from django.core.exceptions import PermissionDenied
from apps.utils.dump import dump
from apps.utils.pagination import paginate_queryset
from apps.utils.superuser_fields import attach_creator_field, apply_creator_field


@login_required
def meeting_list_view(request):
    meetings = get_permitted_objects(request.user, "view", Meeting)
    
    # Pagination using helper function
    meetings_page, pagination_data = paginate_queryset(meetings, request, per_page=50)
    
    return render(request, "meetings/meeting_list.html", {
        "meetings": meetings_page,
        "pagination": pagination_data,
    })


@login_required
def meeting_detail_view(request, pk):
    meeting = get_permitted_object(request.user, "view", Meeting, pk)
    return render(request, "meetings/meeting_detail.html", {"meeting": meeting})


@login_required
def meeting_create_view(request):
    if not is_permitted(request.user, "add", "meetings.meeting"):
        raise PermissionDenied("You do not have permission to add a meeting.")

    if request.method == "POST":
        form = MeetingForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.created_by = request.user
            meeting.save()
            form.save_m2m()
            messages.success(request, "Meeting created successfully.")
            return redirect("meeting_detail", pk=meeting.pk)
    else:
        form = MeetingForm()

    return render(
        request,
        "meetings/meeting_form.html",
        {"form": form},
    )


@login_required
def meeting_edit_view(request, pk):
    meeting = get_permitted_object(request.user, "change", Meeting, pk)

    if request.method == "POST":
        form = MeetingForm(request.POST, instance=meeting)
        attach_creator_field(form, request.user, meeting)
        if form.is_valid():
            form.save()
            apply_creator_field(form, request.user, meeting)
            messages.success(request, "Meeting updated successfully.")
            return redirect("meeting_detail", pk=meeting.pk)
    else:
        form = MeetingForm(instance=meeting)
        attach_creator_field(form, request.user, meeting)

    return render(
        request,
        "meetings/meeting_form.html",
        {"form": form, "meeting": meeting},
    )


@login_required
def meeting_delete_view(request, pk):
    meeting = get_permitted_object(request.user, "delete", Meeting, pk)

    if request.method == "POST":
        meeting.delete()
        messages.success(request, "Meeting deleted successfully!")
        return redirect("meeting_list")

    return render(request, "meetings/meeting_confirm_delete.html", {"meeting": meeting})
