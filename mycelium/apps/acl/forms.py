from django import forms
from django.contrib.auth import get_user_model
from .models import ObjectPermission
from apps.users.utils import get_visible_user_queryset

User = get_user_model()


class ObjectPermissionForm(forms.Form):
    actions = forms.MultipleChoiceField(
        choices=ObjectPermission.ACTION_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )


class UserSelectForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.all().order_by('full_name'),
        label="Select User",
        empty_label="Choose a user...",
        widget=forms.Select(attrs={"class": "w-full"}),
    )

    def __init__(self, *args, current_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user"].queryset = get_visible_user_queryset(current_user).order_by('full_name')
