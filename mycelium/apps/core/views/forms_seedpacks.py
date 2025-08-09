# apps/core/views/forms_seedpacks.py
from django import forms
from django.conf import settings

class SeedpackExportForm(forms.Form):
    name = forms.CharField(
        label="Seedpack name (slug-safe preferred)",
        max_length=64,
        help_text="Used as the folder/zip name."
    )

    # Pick only your project apps (exclude Django contrib)
    APP_CHOICES = [
        (app_label, app_label)
        for app_label in [
            a.split(".")[-1] for a in settings.INSTALLED_APPS
        ]
        if not app_label.startswith("django")
    ]
    apps = forms.MultipleChoiceField(
        label="Include data from apps",
        choices=APP_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

class SeedpackUploadForm(forms.Form):
    file = forms.FileField(label="Upload seedpack .zip")
