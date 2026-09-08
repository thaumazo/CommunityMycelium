from django import forms
from .models import Location, LocationCapital
from apps.capitals.models import Capital
from apps.bioregions.models import Bioregion
from apps.bioregions.utils import get_visible_bioregion_queryset


class LocationForm(forms.ModelForm):
    picture = forms.ImageField(
        required=False,
        label="Location Image",
        help_text="Upload an image representing this location (will be automatically resized)",
    )

    view_members = forms.BooleanField(
        required=False,
        initial=False,
        label="View Members",
        help_text="Check if authenticated members can view this location.",
    )

    view_public = forms.BooleanField(
        required=False,
        initial=False,
        label="View Public",
        help_text="Check if public (unauthenticated) users can view this location.",
    )

    capitals = forms.ModelMultipleChoiceField(
        queryset=Capital.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
        required=False,
        label="Relevant Capitals",
        help_text="Select capitals that are relevant to this location",
    )

    bioregions = forms.ModelMultipleChoiceField(
        queryset=Bioregion.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
        required=False,
        label="Bioregions",
        help_text="Select bioregions associated with this location",
    )

    class Meta:
        model = Location
        fields = [
            "title",
            "description",
            "address",
            "latitude",
            "longitude",
            "bioregions",
            "picture",
            "view_members",
            "view_public",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "address": forms.Textarea(attrs={"rows": 2}),
            "latitude": forms.NumberInput(attrs={"step": "0.000001"}),
            "longitude": forms.NumberInput(attrs={"step": "0.000001"}),
        }

    def __init__(self, *args, current_user=None, **kwargs):
        super().__init__(*args, **kwargs)

        visible_bioregions = get_visible_bioregion_queryset(current_user)
        if self.instance.pk:
            visible_bioregions = visible_bioregions | Bioregion.objects.filter(
                pk__in=self.instance.bioregions.values_list("pk", flat=True)
            )
        self.fields["bioregions"].queryset = visible_bioregions.distinct()

        if self.instance.pk:
            self.fields["capitals"].initial = [
                lc.capital.id for lc in self.instance.location_capital_relationships.all()
            ]

    def save(self, commit=True):
        location = super().save(commit=False)

        location.view_members = self.cleaned_data.get("view_members", False)
        location.view_public = self.cleaned_data.get("view_public", False)

        if commit:
            location.save()
            self.save_m2m()

            selected_capitals = self.cleaned_data.get("capitals", [])
            LocationCapital.objects.filter(location=location).delete()
            for capital in selected_capitals:
                LocationCapital.objects.get_or_create(location=location, capital=capital)

        return location
