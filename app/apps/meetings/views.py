from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Meeting
from .forms import MeetingForm


@login_required
def meeting_list_view(request):
    meetings = Meeting.objects.all().order_by("-start_time")
    return render(request, "meetings/meeting_list.html", {"meetings": meetings})


@login_required
def meeting_detail_view(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
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
        request, "meetings/meeting_form.html", {"form": form, "title": "Create Meeting"}
    )


@login_required
def meeting_edit_view(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)

    # Only allow creator to edit
    if meeting.created_by != request.user:
        messages.error(request, "You don't have permission to edit this meeting.")
        return redirect("meeting_list")

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
    meeting = get_object_or_404(Meeting, pk=pk)

    # Only allow creator to delete
    if meeting.created_by != request.user:
        messages.error(request, "You don't have permission to delete this meeting.")
        return redirect("meeting_list")

    if request.method == "POST":
        meeting.delete()
        messages.success(request, "Meeting deleted successfully!")
        return redirect("meeting_list")

    return render(request, "meetings/meeting_confirm_delete.html", {"meeting": meeting})
