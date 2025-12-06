from django import forms
from .models import Community


class CommunityForm(forms.ModelForm):
    picture = forms.ImageField(
        required=False,
        label="Representative Image",
        help_text="Upload an image representing this community (will be automatically resized)",
    )
    
    view_members = forms.BooleanField(
        required=False,
        initial=False,
        label="View Members",
        help_text="Check if authenticated members can view this community.",
    )

    view_public = forms.BooleanField(
        required=False,
        initial=False,
        label="View Public",
        help_text="Check if public (unauthenticated) users can view this community.",
    )
    
    class Meta:
        model = Community
        fields = ["title", "description", "members", "bioregions", "url", "picture", "view_members", "view_public"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "members": forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
            "bioregions": forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
            "url": forms.Textarea(attrs={"rows": 1}),
        }
