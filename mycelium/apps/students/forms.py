from django import forms
from .models import Student


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["title", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }
