from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Meeting
from .serializers import MeetingSerializer


class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    permission_classes = [IsAuthenticated]
