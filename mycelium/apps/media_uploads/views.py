from rest_framework import generics
from .models import UploadedMedia
from .serializers import UploadedMediaSerializer

class UploadMediaView(generics.CreateAPIView):
    queryset = UploadedMedia.objects.all()
    serializer_class = UploadedMediaSerializer
