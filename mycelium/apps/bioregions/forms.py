from django import forms
from .models import Bioregion


class BioregionForm(forms.ModelForm):
    picture = forms.ImageField(
        required=False,
        label="Representative Image",
        help_text="Upload an image representing this bioregion (will be automatically resized)",
    )
    
    class Meta:
        model = Bioregion
        fields = ["title", "description", "parent_region", "picture"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }


