from django import forms
from django.contrib.auth import get_user_model
from .models import Bioregion

User = get_user_model()


class BioregionForm(forms.ModelForm):
    picture = forms.ImageField(
        required=False,
        label="Representative Image",
        help_text="Upload an image representing this bioregion (will be automatically resized)",
    )

    owners = forms.ModelMultipleChoiceField(
        queryset=User.objects.order_by("username"),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
        label="Owners",
        help_text="Superadmin only: users who can manage this bioregion's admins.",
    )

    admins = forms.ModelMultipleChoiceField(
        queryset=User.objects.order_by("username"),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
        label="Admins",
        help_text="Users who can manage this bioregion's members and visibility settings.",
    )

    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.order_by("username"),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
        label="Members",
        help_text="Users who are members of this bioregion.",
    )

    view_members = forms.BooleanField(
        required=False,
        initial=False,
        label="View Members",
        help_text="Check if any authenticated member can view this bioregion. Users connected to the bioregion can always view it.",
    )

    view_public = forms.BooleanField(
        required=False,
        initial=False,
        label="View Public",
        help_text="Check if public (unauthenticated) users can view this bioregion.",
    )

    class Meta:
        model = Bioregion
        fields = [
            "title",
            "description",
            "parent_region",
            "picture",
            "location",
            "latitude",
            "longitude",
            "radius_km",
            "owners",
            "admins",
            "members",
            "view_members",
            "view_public",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, current_user=None, **kwargs):
        super().__init__(*args, **kwargs)

        is_superuser = bool(current_user and current_user.is_superuser)
        is_owner = bool(
            current_user and self.instance.pk and current_user in self.instance.owners.all()
        )
        is_admin = bool(
            current_user and self.instance.pk and current_user in self.instance.admins.all()
        )

        # Role hierarchy: only superadmins assign owners; owners assign admins; admins assign members.
        if not is_superuser:
            del self.fields["owners"]
        if not (is_superuser or is_owner):
            del self.fields["admins"]
        if not (is_superuser or is_owner or is_admin):
            del self.fields["members"]

