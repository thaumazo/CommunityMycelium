from django.db import models

class UploadedMedia(models.Model):
    MEDIA_TYPES = [
        ('image', 'Image'),
        ('audio', 'Audio'),
    ]
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    file = models.FileField(upload_to='uploads/')
    tags = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
