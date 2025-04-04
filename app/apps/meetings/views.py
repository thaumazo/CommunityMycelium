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
