from django import forms
from django.contrib.auth import get_user_model
from .models import Meeting
from apps.acl.models import ObjectPermission

User = get_user_model()


class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ["title", "start_time", "end_time", "description"]
        widgets = {
            "start_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class MeetingPermissionForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(), label="Select User", empty_label="Choose a user..."
    )
