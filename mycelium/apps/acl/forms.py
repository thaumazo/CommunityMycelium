from django import forms
from django.contrib.auth import get_user_model
from .models import ObjectPermission

User = get_user_model()


class ObjectPermissionForm(forms.Form):
    actions = forms.MultipleChoiceField(
        choices=ObjectPermission.ACTION_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )


class UserSelectForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label="Select User",
        empty_label="Choose a user...",
        widget=forms.Select(attrs={"class": "w-full"}),
    )
