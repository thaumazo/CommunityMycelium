from rest_framework import serializers
from .models import UploadedMedia

class UploadedMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedMedia
        fields = '__all__'
