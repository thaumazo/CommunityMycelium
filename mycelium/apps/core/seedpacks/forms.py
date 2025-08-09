from django import forms
from django.apps import apps

def list_exportable_apps():
    # Filter out contrib + system-ish apps; tweak as needed
    excluded = {"admin", "auth", "contenttypes", "sessions", "messages", "staticfiles"}
    return sorted(
        [a.label for a in apps.get_app_configs() if a.label not in excluded and a.module.__name__.startswith("apps.") ]
    )

class SeedpackExportForm(forms.Form):
    name = forms.CharField(label="Seedpack name", max_length=100)
    apps = forms.MultipleChoiceField(
        label="Apps to export",
        choices=[(a, a) for a in list_exportable_apps()],
        widget=forms.CheckboxSelectMultiple
    )

class SeedpackUploadForm(forms.Form):
    file = forms.FileField(label="Upload seedpack (.zip)")
