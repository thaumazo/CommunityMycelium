from django import forms
from .models import Hat


class HatForm(forms.ModelForm):
    class Meta:
        model = Hat
        fields = ["title", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }
