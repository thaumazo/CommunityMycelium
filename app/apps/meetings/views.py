from rest_framework import viewsets
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Meeting
from .serializers import MeetingSerializer


class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer


@login_required
def meeting_list_view(request):
    meetings = Meeting.objects.all()
    return render(request, "meetings/meeting_list.html", {"meetings": meetings})
