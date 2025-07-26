from django import forms
from .models import Bioregion


class BioregionForm(forms.ModelForm):
    class Meta:
        model = Bioregion
        fields = ["title", "description", "parent_region"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }


