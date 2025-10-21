from django import forms
from .models import Relationship


class RelationshipForm(forms.ModelForm):
    class Meta:
        model = Relationship
        fields = ["title", "description", "resolutions"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "resolutions": forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
        }
