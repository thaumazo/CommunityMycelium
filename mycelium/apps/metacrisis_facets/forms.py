from django import forms
from .models import Metacrisis_facet


class Metacrisis_facetForm(forms.ModelForm):
    class Meta:
        model = Metacrisis_facet
        fields = ["title", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }
