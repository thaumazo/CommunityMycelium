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
        fields = [
            "title",
            "description",
            "phase",
            "state",
            "members",
            "owners",
            "admins",
            "bioregions",
            "url",
            "view_members",
            "view_public",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "phase": forms.Select(attrs={"class": "w-full"}),
            "state": forms.Select(attrs={"class": "w-full"}),
            "members": forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
            "owners": forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
            "admins": forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
            "bioregions": forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
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
            
            # Handle capitals_in through model - sync instead of delete/recreate
            selected_capitals_in = set(self.cleaned_data.get('capitals_in', []))
            existing_capitals_in = set(
                pc.capital for pc in ProjectCapitalIn.objects.filter(project=project).select_related('capital')
            )
            
            # Remove capitals that are no longer selected
            capitals_to_remove_in = existing_capitals_in - selected_capitals_in
            if capitals_to_remove_in:
                ProjectCapitalIn.objects.filter(
                    project=project, 
                    capital__in=capitals_to_remove_in
                ).delete()
            
            # Add new capitals
            capitals_to_add_in = selected_capitals_in - existing_capitals_in
            for capital in capitals_to_add_in:
                ProjectCapitalIn.objects.create(project=project, capital=capital)
            
            # Handle capitals_out through model - sync instead of delete/recreate
            selected_capitals_out = set(self.cleaned_data.get('capitals_out', []))
            existing_capitals_out = set(
                pc.capital for pc in ProjectCapitalOut.objects.filter(project=project).select_related('capital')
            )
            
            # Remove capitals that are no longer selected
            capitals_to_remove_out = existing_capitals_out - selected_capitals_out
            if capitals_to_remove_out:
                ProjectCapitalOut.objects.filter(
                    project=project, 
                    capital__in=capitals_to_remove_out
                ).delete()
            
            # Add new capitals
            capitals_to_add_out = selected_capitals_out - existing_capitals_out
            for capital in capitals_to_add_out:
                ProjectCapitalOut.objects.create(project=project, capital=capital)
        
        return project
