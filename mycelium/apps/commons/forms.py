from django import forms
from django.contrib.auth import get_user_model
from .models import Commons
from apps.bioregions.models import Bioregion
from apps.bioregions.utils import get_visible_bioregion_queryset
from apps.users.utils import get_visible_user_queryset

User = get_user_model()


class CommonsForm(forms.ModelForm):
    owners = forms.ModelMultipleChoiceField(
        queryset=User.objects.order_by("username"),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
        label="Owners",
        help_text="Superadmin only: users who can manage this commons' admins.",
    )

    admins = forms.ModelMultipleChoiceField(
        queryset=User.objects.order_by("username"),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
        label="Admins",
        help_text="Users who can manage this commons' members, applications and invites.",
    )

    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.order_by("username"),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
        label="Members",
        help_text="Users who are members of this commons.",
    )

    view_members = forms.BooleanField(
        required=False,
        initial=False,
        label="View Members",
        help_text="Check if any authenticated member can view this commons.",
    )

    view_public = forms.BooleanField(
        required=False,
        initial=False,
        label="View Public",
        help_text="Check if public (unauthenticated) users can view this commons.",
    )

    class Meta:
        model = Commons
        fields = [
            "title",
            "description",
            "bioregion",
            "agreements_url",
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

        visible_users = get_visible_user_queryset(current_user)
        for field_name in ("owners", "admins", "members"):
            if field_name not in self.fields:
                continue
            field_users = visible_users
            if self.instance.pk:
                field_users = field_users | User.objects.filter(
                    pk__in=getattr(self.instance, field_name).values_list("pk", flat=True)
                )
            self.fields[field_name].queryset = field_users.distinct().order_by("username")

        visible_bioregions = get_visible_bioregion_queryset(current_user)
        if self.instance.pk and self.instance.bioregion_id:
            visible_bioregions = visible_bioregions | Bioregion.objects.filter(pk=self.instance.bioregion_id)
        self.fields["bioregion"].queryset = visible_bioregions.distinct().order_by("title")
        self.fields["bioregion"].required = False


class CommonsApplicationForm(forms.Form):
    note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        label="Note",
        help_text="Optional note to the commons owners/admins.",
    )


class CommonsInviteForm(forms.Form):
    invited_user = forms.ModelChoiceField(
        queryset=User.objects.order_by("username"),
        label="Invite person",
    )

    def __init__(self, *args, commons=None, **kwargs):
        super().__init__(*args, **kwargs)
        if commons is not None:
            existing_member_ids = commons.members.values_list("pk", flat=True)
            self.fields["invited_user"].queryset = User.objects.exclude(
                pk__in=existing_member_ids
            ).order_by("username")
