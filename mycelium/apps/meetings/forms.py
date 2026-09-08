from django import forms
from .models import Meeting
from apps.users.utils import get_visible_user_queryset


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

    def __init__(self, *args, current_user=None, **kwargs):
        super().__init__(*args, **kwargs)

        visible_users = get_visible_user_queryset(current_user)
        if self.instance.pk:
            visible_users = visible_users | self.instance.attending.model.objects.filter(
                pk__in=self.instance.attending.values_list("pk", flat=True)
            )
        self.fields["attending"].queryset = visible_users.distinct()
