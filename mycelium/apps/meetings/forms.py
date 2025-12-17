from django import forms
from .models import Meeting


class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = [
            "title", "start_time", "end_time", "description", "attending", 
            "url", "youtube_url", "transcript_gdrive_url", "transcript_gdrive_folder_id",
            "transcript"
        ]
        widgets = {
            "start_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_time": forms.DateTimeInput(attrs={"type": "datetime-local", "required": False}),
            "description": forms.Textarea(attrs={"rows": 4}),
            "attending": forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
            "url": forms.Textarea(attrs={"rows": 1}),
            "youtube_url": forms.URLInput(attrs={"placeholder": "https://youtube.com/watch?v=..."}),
            "transcript_gdrive_url": forms.URLInput(attrs={"placeholder": "https://drive.google.com/file/d/..."}),
            "transcript_gdrive_folder_id": forms.TextInput(attrs={"placeholder": "Google Drive folder ID"}),
            "transcript": forms.Textarea(attrs={"rows": 6, "placeholder": "Enter meeting transcript here..."}),
        }
