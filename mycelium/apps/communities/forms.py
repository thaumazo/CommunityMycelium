from django import forms
from .models import Community
from apps.locations.models import Location


class CommunityForm(forms.ModelForm):
    picture = forms.ImageField(
        required=False,
        label="Representative Image",
        help_text="Upload an image representing this community (will be automatically resized)",
    )
    
    view_members = forms.BooleanField(
        required=False,
        initial=False,
        label="View Members",
        help_text="Check if authenticated members can view this community.",
    )

    view_public = forms.BooleanField(
        required=False,
        initial=False,
        label="View Public",
        help_text="Check if public (unauthenticated) users can view this community.",
    )

    primary_location = forms.ModelChoiceField(
        queryset=Location.objects.all().order_by("title"),
        required=False,
        label="Primary Location",
        help_text="Primary map location for this community",
    )

    locations = forms.ModelMultipleChoiceField(
        queryset=Location.objects.all().order_by("title"),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
        required=False,
        label="Locations",
        help_text="Locations connected to this community",
    )
    
    class Meta:
        model = Community
        fields = [
            "title",
            "description",
            "members",
            "owners",
            "admins",
            "bioregions",
            "primary_location",
            "locations",
            "url",
            "picture",
            "view_members",
            "view_public",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "members": forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
            "owners": forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
            "admins": forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
            "bioregions": forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
            "url": forms.Textarea(attrs={"rows": 1}),
        }

    def clean(self):
        cleaned = super().clean()
        primary_location = cleaned.get("primary_location")
        locations = cleaned.get("locations")
        if primary_location and locations is not None and primary_location not in locations:
            cleaned["locations"] = locations | Location.objects.filter(pk=primary_location.pk)
        return cleaned

    def save(self, commit=True):
        community = super().save(commit=commit)
        if commit:
            primary_location = self.cleaned_data.get("primary_location")
            if primary_location:
                community.locations.add(primary_location)
        return community
