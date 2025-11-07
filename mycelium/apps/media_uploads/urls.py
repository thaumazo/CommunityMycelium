from django.urls import path
from .views import UploadMediaView

urlpatterns = [
    path('api/upload-media/', UploadMediaView.as_view(), name='upload-media'),
]
