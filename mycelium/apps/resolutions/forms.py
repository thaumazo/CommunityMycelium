from django import forms
from .models import Resolution


class ResolutionForm(forms.ModelForm):
    class Meta:
        model = Resolution
        fields = ["title", "description", "url"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "url": forms.Textarea(attrs={"rows": 1}),
        }
