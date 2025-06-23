from django import forms
from .models import Community


class CommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ["title", "description", "members", "url"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "members": forms.SelectMultiple(attrs={"class": "w-full"}),
            "url": forms.Textarea(attrs={"rows": 1}),
        }
