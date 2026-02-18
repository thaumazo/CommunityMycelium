from django import forms
from apps.resolutions.models import Resolution
from .models import Relationship, RelationshipProposal


class RelationshipForm(forms.ModelForm):
    class Meta:
        model = Relationship
        fields = ["title", "description", "resolutions"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "resolutions": forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
        }


class RelationshipProposalForm(forms.ModelForm):
    from_person = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label="On Behalf Of (Person)",
    )
    from_community = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label="On Behalf Of (Organization)",
    )
    from_project = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label="On Behalf Of (Project)",
    )
    to_person = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label="To (Person)",
    )
    to_community = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label="To (Organization)",
    )
    to_project = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label="To (Project)",
    )
    resolution = forms.ModelChoiceField(
        queryset=Resolution.objects.all(),
        required=True,
        label="Resolution",
    )

    class Meta:
        model = RelationshipProposal
        fields = [
            "relationship_type",
            "note",
            "resolution",
            "from_person",
            "from_community",
            "from_project",
            "to_person",
            "to_community",
            "to_project",
        ]
        widgets = {
            "note": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        from_people = kwargs.pop("from_people", None)
        from_communities = kwargs.pop("from_communities", None)
        from_projects = kwargs.pop("from_projects", None)
        to_people = kwargs.pop("to_people", None)
        to_communities = kwargs.pop("to_communities", None)
        to_projects = kwargs.pop("to_projects", None)
        super().__init__(*args, **kwargs)
        if from_people is not None:
            self.fields["from_person"].queryset = from_people
        if from_communities is not None:
            self.fields["from_community"].queryset = from_communities
        if from_projects is not None:
            self.fields["from_project"].queryset = from_projects
        if to_people is not None:
            self.fields["to_person"].queryset = to_people
        if to_communities is not None:
            self.fields["to_community"].queryset = to_communities
        if to_projects is not None:
            self.fields["to_project"].queryset = to_projects

    def clean(self):
        cleaned = super().clean()
        from_targets = [
            cleaned.get("from_person"),
            cleaned.get("from_community"),
            cleaned.get("from_project"),
        ]
        to_targets = [
            cleaned.get("to_person"),
            cleaned.get("to_community"),
            cleaned.get("to_project"),
        ]
        if sum(1 for target in from_targets if target is not None) != 1:
            raise forms.ValidationError("Select exactly one from-party.")
        if sum(1 for target in to_targets if target is not None) != 1:
            raise forms.ValidationError("Select exactly one to-party.")
        return cleaned


class RelationshipProposalResponseForm(forms.Form):
    note = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}), required=False)
    resolution = forms.ModelChoiceField(queryset=Resolution.objects.all(), required=False)
