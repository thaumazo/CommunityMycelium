from django import forms
from apps.communities.models import Community
from apps.hats.models import Hat
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
        fields = ["username", "email", "full_name"]
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
            self.save_m2m()  # save many to many fields

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

    user_location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "w-full"}),
        label="Location",
    )

    invited_by = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={"class": "w-full"}),
        required=False,
        label="Invited by",
    )

    user_communities = forms.ModelMultipleChoiceField(
        queryset=Community.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
        required=False,
        label="Communities",
    )

    user_hats = forms.ModelMultipleChoiceField(
        queryset=Hat.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
        required=False,
        label="Hats",
    )

    linked_in = forms.URLField(
        required=False,
        widget=forms.TextInput(attrs={"class": "w-full"}),
        label="LinkedIn URL",
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "full_name",
            "user_location",
            "invited_by",
            "user_communities",
            "user_hats",
            "linked_in",
        ]
        widgets = {
            "username": forms.TextInput(),
        }


class UserPasswordChangeForm(forms.Form):
    """Separate form for changing user passwords."""

    password = forms.CharField(
        widget=forms.PasswordInput(),
        min_length=8,
        help_text="Password must be at least 8 characters long.",
        required=True,
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(), label="Confirm Password", required=True
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match")

        return cleaned_data

    def save(self, user):
        """Update the user's password."""
        user.set_password(self.cleaned_data["password"])
        user.save()
        return user


class UserPermissionForm(forms.Form):
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Access",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.user and self.user.pk:
            # Set the initial value to all user's groups
            self.fields["groups"].initial = self.user.groups.all()

    def clean(self):
        cleaned_data = super().clean()
        groups = cleaned_data.get("groups", [])

        # If Admin is selected, remove all other groups
        admin_group = Group.objects.filter(name="Admin").first()
        if admin_group in groups:
            cleaned_data["groups"] = [admin_group]

        return cleaned_data
