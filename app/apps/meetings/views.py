from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from apps.acl.utils import get_permitted_objects, get_permitted_object
from .models import Meeting
from .forms import MeetingForm


@login_required
def meeting_list_view(request):
    meetings = get_permitted_objects(request.user, "view", Meeting)
    return render(request, "meetings/meeting_list.html", {"meetings": meetings})


@login_required
def meeting_calendar_view(request):
    return render(request, "meetings/meeting_calendar.html")


@login_required
def meeting_calendar_events(request):
    meetings = get_permitted_objects(request.user, "view", Meeting)
    events = []
    for meeting in meetings:
        events.append({
            'id': meeting.id,
            'title': meeting.title,
            'start': meeting.start_time.isoformat(),
            'end': meeting.end_time.isoformat(),
            'url': f'/meetings/{meeting.id}/',
            'description': meeting.description,
            'created_by': meeting.created_by.username,
        })
    return JsonResponse(events, safe=False)


@login_required
def meeting_detail_view(request, pk):
    meeting = get_permitted_object(request.user, "view", Meeting, pk)
    return render(request, "meetings/meeting_detail.html", {"meeting": meeting})


@login_required
def meeting_create_view(request):
    if request.method == "POST":
        form = MeetingForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.created_by = request.user
            meeting.save()
            messages.success(request, "Meeting created successfully!")
            return redirect("meeting_list")
    else:
        form = MeetingForm()

    return render(
        request,
        "meetings/meeting_form.html",
        {"form": form, "title": "Create Meeting"},
    )


@login_required
def meeting_edit_view(request, pk):
    meeting = get_permitted_object(request.user, "change", Meeting, pk)

    if request.method == "POST":
        form = MeetingForm(request.POST, instance=meeting)
        if form.is_valid():
            form.save()
            messages.success(request, "Meeting updated successfully!")
            return redirect("meeting_list")
    else:
        form = MeetingForm(instance=meeting)

    return render(
        request,
        "meetings/meeting_form.html",
        {"form": form, "title": "Edit Meeting", "meeting": meeting},
    )


@login_required
def meeting_delete_view(request, pk):
    meeting = get_permitted_object(request.user, "delete", Meeting, pk)

    if request.method == "POST":
        meeting.delete()
        messages.success(request, "Meeting deleted successfully!")
        return redirect("meeting_list")

    return render(request, "meetings/meeting_confirm_delete.html", {"meeting": meeting})
