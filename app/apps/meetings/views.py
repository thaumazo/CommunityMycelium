from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Meeting


@login_required
def meeting_list_view(request):
    meetings = Meeting.objects.all()
    return render(request, "meetings/meeting_list.html", {"meetings": meetings})
