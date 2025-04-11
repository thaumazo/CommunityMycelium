from django import forms
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["is_viewer", "is_editor", "is_admin"]
        widgets = {
            "is_viewer": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_editor": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_admin": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
