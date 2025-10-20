from django import forms
from .models import Challenge


class ChallengeForm(forms.ModelForm):
    class Meta:
        model = Challenge
        fields = [
            "title",
            "description",
            "related_facet",
            "level",
            "related_bioregion",
            "location",
            "latitude",
            "longitude",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "related_facet": forms.Select(),
            "related_bioregion": forms.Select(),
        }


