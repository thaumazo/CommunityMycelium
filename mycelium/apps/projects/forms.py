from django import forms
from .models import Project


class ProjectForm(forms.ModelForm):
    view_members = forms.BooleanField(
        required=False,
        initial=False,
        label="View Members",
        help_text="Check if authenticated members can view this project.",
    )

    view_public = forms.BooleanField(
        required=False,
        initial=False,
        label="View Public",
        help_text="Check if public (unauthenticated) users can view this project.",
    )
    
    class Meta:
        model = Project
        fields = ["title", "description", "members", "url", "view_members", "view_public"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "members": forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
            "url": forms.Textarea(attrs={"rows": 1}),
        }
