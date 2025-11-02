from django import forms
from apps.bioregions.models import Bioregion
from apps.communities.models import Community
from apps.relationships.models import Relationship
from apps.socialroles.models import Socialrole
from apps.maladaptives.models import Maladaptive
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

    user_bioregions = forms.ModelMultipleChoiceField(
        queryset=Bioregion.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
        required=False,
        label="Bioregions",
    )

    user_communities = forms.ModelMultipleChoiceField(
        queryset=Community.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
        required=False,
        label="Communities",
    )

    user_relationships = forms.ModelMultipleChoiceField(
        queryset=Relationship.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
        required=False,
        label="Relationships",
    )

    user_socialroles = forms.ModelMultipleChoiceField(
        queryset=Socialrole.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
        required=False,
        label="Social Roles",
    )

    user_maladaptives = forms.ModelMultipleChoiceField(
        queryset=Maladaptive.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
        required=False,
        label="Maladaptive Schemas",
    )

    linked_in = forms.URLField(
        required=False,
        widget=forms.TextInput(attrs={"class": "w-full"}),
        label="LinkedIn URL",
    )

    # NEW: optional password fields (for admin create/edit)
    password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        label="Password (optional)",
        help_text="Leave blank to keep the existing password.",
        min_length=8,
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        label="Confirm Password",
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "full_name",
            "user_location",
            "invited_by",
            "user_bioregions",
            "user_communities",
            "user_relationships",
            "user_socialroles",
            "user_maladaptives",
            "linked_in",
            # password fields are not model fields; they’re above
        ]
        widgets = {
            "username": forms.TextInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # If editing, don't allow "invited_by" to be self
        if self.instance and self.instance.pk:
            self.fields["invited_by"].queryset = User.objects.exclude(pk=self.instance.pk)

    def clean(self):
        cleaned = super().clean()
        pwd = cleaned.get("password") or ""
        cpw = cleaned.get("confirm_password") or ""
        # Only validate if a password was provided
        if pwd or cpw:
            if pwd != cpw:
                raise forms.ValidationError("Passwords don't match.")
            if len(pwd) < 8:
                raise forms.ValidationError("Password must be at least 8 characters long.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        pwd = self.cleaned_data.get("password")

        if pwd:
            user.set_password(pwd)

        if commit:
            user.save()
            self.save_m2m()

        return user

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
