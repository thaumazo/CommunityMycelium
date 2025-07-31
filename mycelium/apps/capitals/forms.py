from django import forms
from .models import Capital


class CapitalForm(forms.ModelForm):
    class Meta:
        model = Capital
        fields = ["title", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }
