from django import forms
from .models import Project, ProjectCapitalIn, ProjectCapitalOut
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
        fields = ["title", "description", "members", "url", "view_members", "view_public"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "members": forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
            "url": forms.Textarea(attrs={"rows": 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set initial values for capitals from through models
        if self.instance.pk:
            self.fields['capitals_in'].initial = [
                pc.capital.id for pc in self.instance.project_capital_in_relationships.all()
            ]
            self.fields['capitals_out'].initial = [
                pc.capital.id for pc in self.instance.project_capital_out_relationships.all()
            ]

    def save(self, commit=True):
        project = super().save(commit=False)
        
        # Explicitly handle view_members and view_public fields
        project.view_members = self.cleaned_data.get("view_members", False)
        project.view_public = self.cleaned_data.get("view_public", False)
        
        if commit:
            project.save()
            self.save_m2m()
            
            # Handle capitals_in through model
            selected_capitals_in = self.cleaned_data.get('capitals_in', [])
            ProjectCapitalIn.objects.filter(project=project).delete()
            for capital in selected_capitals_in:
                ProjectCapitalIn.objects.get_or_create(project=project, capital=capital)
            
            # Handle capitals_out through model
            selected_capitals_out = self.cleaned_data.get('capitals_out', [])
            ProjectCapitalOut.objects.filter(project=project).delete()
            for capital in selected_capitals_out:
                ProjectCapitalOut.objects.get_or_create(project=project, capital=capital)
        
        return project
