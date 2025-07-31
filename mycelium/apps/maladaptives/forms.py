from django import forms
from .models import Maladaptive


class MaladaptiveForm(forms.ModelForm):
    class Meta:
        model = Maladaptive
        fields = ["title", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }
