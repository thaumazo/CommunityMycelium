from django import forms
from .models import Meeting


class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ["title", "start_time", "end_time", "description", "attending", "url", "transcript"]
        widgets = {
            "start_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "description": forms.Textarea(attrs={"rows": 4}),
            "attending": forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
            "url": forms.Textarea(attrs={"rows": 1}),
            "transcript": forms.Textarea(attrs={"rows": 6, "placeholder": "Enter meeting transcript here..."}),
        }
