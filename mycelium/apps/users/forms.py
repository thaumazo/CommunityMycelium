from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group

User = get_user_model()


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())


class RegisterForm(forms.ModelForm):
    full_name = forms.CharField(
        widget=forms.TextInput(),
        label="Full Name",
        help_text="Enter your full name.",
        required=True,
    )
    email = forms.EmailField(
        widget=forms.EmailInput(),
        help_text="Enter your email address.",
        required=True,
    )
    password = forms.CharField(
        widget=forms.PasswordInput(),
        min_length=8,
        help_text="Password must be at least 8 characters long.",
        required=True,
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(), label="Confirm Password", required=True
    )

    class Meta:
        model = User
        fields = ["username", "email", "full_name", "password"]
        widgets = {
            "username": forms.TextInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()

        return user


class UserForm(forms.ModelForm):
    full_name = forms.CharField(
        widget=forms.TextInput(),
        label="Full Name",
        help_text="Enter your full name.",
        required=True,
    )
    email = forms.EmailField(
        widget=forms.EmailInput(),
        help_text="Enter your email address.",
        required=True,
    )

    # Note that password and confirm_password are optional
    # because we don't want to force a password change on edit.
    password = forms.CharField(
        widget=forms.PasswordInput(),
        min_length=8,
        help_text="Password must be at least 8 characters long.",
        required=False,
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(), label="Confirm Password", required=False
    )

    class Meta:
        model = User
        fields = ["username", "email", "full_name", "password"]
        widgets = {
            "username": forms.TextInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()

        return user


class UserPermissionForm(forms.Form):
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Roles",
        required=False
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.user and self.user.pk:
            # Set the initial value to all user's groups
            self.fields["groups"].initial = self.user.groups.all()
