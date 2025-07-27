from django import forms
from .models import Socialrole


class SocialroleForm(forms.ModelForm):
    class Meta:
        model = Socialrole
        fields = ["title", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }
