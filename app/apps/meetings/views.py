from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Meeting
from .forms import MeetingForm


def meeting_list_view(request):
    meetings = Meeting.objects.all()
    return render(request, "meetings/meeting_list.html", {"meetings": meetings})


def meeting_detail_view(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    return render(request, "meetings/meeting_detail.html", {"meeting": meeting})


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


def meeting_edit_view(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)

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


def meeting_delete_view(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)

    if request.method == "POST":
        meeting.delete()
        messages.success(request, "Meeting deleted successfully!")
        return redirect("meeting_list")

    return render(request, "meetings/meeting_confirm_delete.html", {"meeting": meeting})
