from django import forms
from .models import Project, ProjectCapitalIn, ProjectCapitalOut
from apps.capitals.models import Capital
from apps.locations.models import Location


class ProjectForm(forms.ModelForm):
    time_precision = forms.ChoiceField(
        choices=Project.TIME_PRECISION_CHOICES,
        required=False,
        initial=Project.TIME_PRECISION_NONE,
        label="Time Precision",
        help_text="Whether this move happens at a single point in time or over a range.",
    )

    project_start_at = forms.DateTimeField(
        required=False,
        label="Project Start",
        help_text="Optional start date/time for this move.",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
        input_formats=["%Y-%m-%dT%H:%M"],
    )

    project_end_at = forms.DateTimeField(
        required=False,
        label="Project End",
        help_text="Optional end date/time for this move.",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
        input_formats=["%Y-%m-%dT%H:%M"],
    )

    view_members = forms.BooleanField(
        required=False,
        initial=False,
        label="View Members",
        help_text="Check if authenticated members can view this move.",
    )

    view_public = forms.BooleanField(
        required=False,
        initial=False,
        label="View Public",
        help_text="Check if public (unauthenticated) users can view this move.",
    )
    
    capitals_in = forms.ModelMultipleChoiceField(
        queryset=Capital.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
        required=False,
        label="Capitals In",
        help_text="Select capitals that this move takes in or uses"
    )
    
    capitals_out = forms.ModelMultipleChoiceField(
        queryset=Capital.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
        required=False,
        label="Capitals Out",
        help_text="Select capitals that this move produces or outputs"
    )

    primary_location = forms.ModelChoiceField(
        queryset=Location.objects.all().order_by("title"),
        required=False,
        label="Primary Location",
        help_text="Primary map location for this move",
    )

    locations = forms.ModelMultipleChoiceField(
        queryset=Location.objects.all().order_by("title"),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
        required=False,
        label="Locations",
        help_text="Locations connected to this move",
    )
    
    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "parent",
            "time_precision",
            "project_start_at",
            "project_end_at",
            "phase",
            "state",
            "members",
            "owners",
            "admins",
            "bioregions",
            "primary_location",
            "locations",
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

    def clean(self):
        cleaned = super().clean()
        project_start_at = cleaned.get("project_start_at")
        project_end_at = cleaned.get("project_end_at")
        time_precision = cleaned.get("time_precision") or Project.TIME_PRECISION_NONE
        parent = cleaned.get("parent")
        primary_location = cleaned.get("primary_location")
        locations = cleaned.get("locations")

        if self.instance.pk and parent and parent.pk == self.instance.pk:
            self.add_error("parent", "A move cannot be its own parent.")

        ancestor = parent
        while ancestor is not None and self.instance.pk:
            if ancestor.pk == self.instance.pk:
                self.add_error("parent", "Parent relationship creates a cycle.")
                break
            ancestor = ancestor.parent

        if project_end_at and not project_start_at:
            self.add_error("project_start_at", "Project start is required when project end is set.")
        if project_start_at and project_end_at and project_end_at < project_start_at:
            self.add_error("project_end_at", "Project end must be after project start.")

        if time_precision == Project.TIME_PRECISION_POINT and project_end_at:
            self.add_error("project_end_at", "Point-in-time projects should not set an end time.")
        if time_precision == Project.TIME_PRECISION_RANGE and not project_end_at:
            self.add_error("project_end_at", "Range projects require an end time.")
        if time_precision == Project.TIME_PRECISION_NONE and (project_start_at or project_end_at):
            self.add_error("time_precision", "Set time precision to point or range when time fields are used.")

        if primary_location and locations is not None and primary_location not in locations:
            cleaned["locations"] = locations | Location.objects.filter(pk=primary_location.pk)

        return cleaned

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["parent"].required = False
        self.fields["parent"].label = "Parent Move"
        self.fields["parent"].help_text = "Optional parent move. Leave blank for a top-level move."
        self.fields["parent"].queryset = Project.objects.order_by("title")
        if self.instance.pk:
            self.fields["parent"].queryset = self.fields["parent"].queryset.exclude(pk=self.instance.pk)
        
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

            primary_location = self.cleaned_data.get("primary_location")
            if primary_location:
                project.locations.add(primary_location)
            
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
