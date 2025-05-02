from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group

User = get_user_model()


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())


class UserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(),
        min_length=8,
        help_text="Password must be at least 8 characters long.",
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(), label="Confirm Password"
    )

    class Meta:
        model = User
        fields = ["username", "email", "password"]
        widgets = {
            "username": forms.TextInput(),
            "email": forms.EmailInput(),
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
    groups = forms.ModelChoiceField(
        queryset=Group.objects.all(), widget=forms.Select, label="Role", required=False
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.user and self.user.pk:
            # Set the initial value to the user's first group
            user_groups = self.user.groups.all()
            if user_groups.exists():
                self.fields["groups"].initial = user_groups.first()
