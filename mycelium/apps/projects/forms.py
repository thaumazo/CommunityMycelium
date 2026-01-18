from django import forms
from .models import Project
from apps.capitals.models import Capital


class ProjectForm(forms.ModelForm):
    view_members = forms.BooleanField(
        required=False,
        initial=False,
        label="View Members",
        help_text="Check if authenticated members can view this project.",
    )

    view_public = forms.BooleanField(
        required=False,
        initial=False,
        label="View Public",
        help_text="Check if public (unauthenticated) users can view this project.",
    )
    
    capitals_in = forms.ModelMultipleChoiceField(
        queryset=Capital.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
        required=False,
        label="Capitals In",
        help_text="Select capitals that this project takes in or uses"
    )
    
    capitals_out = forms.ModelMultipleChoiceField(
        queryset=Capital.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
        required=False,
        label="Capitals Out",
        help_text="Select capitals that this project produces or outputs"
    )
    
    class Meta:
        model = Project
        fields = ["title", "description", "members", "url", "view_members", "view_public", "capitals_in", "capitals_out"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "members": forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
            "url": forms.Textarea(attrs={"rows": 1}),
        }

    def save(self, commit=True):
        project = super().save(commit=False)
        
        # Explicitly handle view_members and view_public fields
        project.view_members = self.cleaned_data.get("view_members", False)
        project.view_public = self.cleaned_data.get("view_public", False)
        
        if commit:
            project.save()
            self.save_m2m()
        
        return project
