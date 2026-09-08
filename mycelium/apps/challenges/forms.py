from django import forms
from .models import Challenge
from apps.bioregions.models import Bioregion
from apps.bioregions.utils import get_visible_bioregion_queryset


class ChallengeForm(forms.ModelForm):
    class Meta:
        model = Challenge
        fields = [
            "title",
            "description",
            "related_facet",
            "level",
            "related_bioregion",
            "location",
            "latitude",
            "longitude",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "related_facet": forms.Select(),
            "related_bioregion": forms.Select(),
        }

    def __init__(self, *args, current_user=None, **kwargs):
        super().__init__(*args, **kwargs)

        visible_bioregions = get_visible_bioregion_queryset(current_user)
        if self.instance.pk and self.instance.related_bioregion_id:
            visible_bioregions = visible_bioregions | Bioregion.objects.filter(
                pk=self.instance.related_bioregion_id
            )
        self.fields["related_bioregion"].queryset = visible_bioregions.distinct()


