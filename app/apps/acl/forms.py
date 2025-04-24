from django import forms
from .models import ObjectPermission


class ObjectPermissionForm(forms.Form):
    actions = forms.MultipleChoiceField(
        choices=ObjectPermission.ACTION_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
