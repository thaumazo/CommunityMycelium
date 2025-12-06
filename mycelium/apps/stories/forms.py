from django import forms
from .models import Story, StoryMedia, StoryAttachment


class StoryForm(forms.ModelForm):
    view_members = forms.BooleanField(
        required=False,
        initial=False,
        label="View Members",
        help_text="Check if authenticated members can view this story.",
    )

    view_public = forms.BooleanField(
        required=False,
        initial=False,
        label="View Public",
        help_text="Check if public (unauthenticated) users can view this story.",
    )
    
    class Meta:
        model = Story
        fields = ["title", "text_content", "view_members", "view_public"]
        widgets = {
            "text_content": forms.Textarea(attrs={"rows": 8}),
        }


class StoryMediaForm(forms.ModelForm):
    class Meta:
        model = StoryMedia
        fields = ["media_type", "file", "url", "caption", "order"]
        widgets = {
            "caption": forms.Textarea(attrs={"rows": 3}),
        }
