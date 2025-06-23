from django import forms
from .models import Agreement


class AgreementForm(forms.ModelForm):
    class Meta:
        model = Agreement
        fields = ["title", "description", "url"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "url": forms.Textarea(attrs={"rows": 1}),
        }
