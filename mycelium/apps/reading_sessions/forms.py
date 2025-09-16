from django import forms
from .models import ReadingSession

class ReadingSessionForm(forms.ModelForm):
    class Meta:
        model = ReadingSession
        fields = ['student', 'title', 'date', 'audio']