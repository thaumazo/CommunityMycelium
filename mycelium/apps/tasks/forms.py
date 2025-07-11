from django import forms
from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "due_date", "description", "status", "assigned_to"]
        widgets = {
            "due_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "description": forms.Textarea(attrs={"rows": 4}),
            "assigned_to": forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
        }
