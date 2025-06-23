from django import forms
from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["title", "description", "members", "url"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "members": forms.SelectMultiple(attrs={"class": "w-full"}),
            "url": forms.Textarea(attrs={"rows": 1}),
        }
