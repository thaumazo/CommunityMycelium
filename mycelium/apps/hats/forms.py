from django import forms
from .models import Hat


class HatForm(forms.ModelForm):
    class Meta:
        model = Hat
        fields = ["title", "description", "agreements"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "agreements": forms.SelectMultiple(attrs={"class": "w-full"}),
        }
