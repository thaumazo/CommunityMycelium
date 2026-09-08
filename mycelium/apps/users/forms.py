from django import forms
from apps.bioregions.models import Bioregion
from apps.bioregions.utils import get_visible_bioregion_queryset
from apps.communities.models import Community
from apps.relationships.models import Relationship
from apps.socialroles.models import Socialrole
from apps.metacrisis_facets.models import Metacrisis_facet
from apps.maladaptives.models import Maladaptive
from apps.locations.models import Location
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group
from django.utils.text import slugify

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

    view_members = forms.BooleanField(
        required=False,
        initial=False,
        label="View Members",
        help_text="Allow viewing members.",
    )

    view_public = forms.BooleanField(
        required=False,
        initial=False,
        label="View Public",
        help_text="Allow viewing public content.",
    )

    ai_transcript_processing = forms.BooleanField(
        required=False,
        initial=False,
        label="AI Transcript Processing",
        help_text="Allow AI (like GPT in temporary mode) to analyze meeting transcripts to make connections between people and extract useful tasks.",
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
        queryset=User.objects.all().order_by('full_name'),
        widget=forms.Select(attrs={"class": "w-full"}),
        required=False,
        label="Invited by",
    )

    invite_role = forms.ChoiceField(
        choices=User.INVITE_ROLE_CHOICES,
        required=False,
        label="Invite Role",
        help_text="Can Invite can generate invites. Can Approve can invite and approve registrations.",
    )

    primary_location = forms.ModelChoiceField(
        queryset=Location.objects.all().order_by("title"),
        widget=forms.Select(attrs={"class": "w-full"}),
        required=False,
        label="Primary Location",
    )

    user_locations = forms.ModelMultipleChoiceField(
        queryset=Location.objects.all().order_by("title"),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
        required=False,
        label="Locations",
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

    user_metacrisis_facets = forms.ModelMultipleChoiceField(
        queryset=Metacrisis_facet.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
        required=False,
        label="Metacrisis Facets",
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

    alternate_deck = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "w-full", "placeholder": "moore"}),
        label="Alternate Deck",
        help_text="Optional deck subfolder name; it will be normalized to lowercase slug format.",
    )
    
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "w-full", "rows": 4}),
        label="Biography",
        help_text="Tell us about yourself",
    )

    picture = forms.ImageField(
        required=False,
        label="Profile Picture",
        help_text="Upload a profile picture (will be automatically resized)",
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

    view_members = forms.BooleanField(
        required=False,
        initial=False,
        label="View Members",
        help_text="Allow viewing members.",
    )

    view_public = forms.BooleanField(
        required=False,
        initial=False,
        label="View Public",
        help_text="Allow viewing public content.",
    )

    ai_transcript_processing = forms.BooleanField(
        required=False,
        initial=False,
        label="AI Transcript Processing",
        help_text="Allow AI (like GPT in temporary mode) to analyze meeting transcripts to make connections between people and extract useful tasks.",
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "full_name",
            "user_location",
            "invited_by",
            "invite_role",
            "primary_location",
            "user_locations",
            "user_bioregions",
            "user_communities",
            "user_relationships",
            "user_socialroles",
            "user_metacrisis_facets",
            "user_maladaptives",
            "linked_in",
            "alternate_deck",
            "bio",
            "picture",
            # password fields are not model fields; they're above
        ]
        widgets = {
            "username": forms.TextInput(),
        }

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop("current_user", None)
        super().__init__(*args, **kwargs)

        visible_bioregions = get_visible_bioregion_queryset(self.current_user)
        if self.instance.pk:
            visible_bioregions = visible_bioregions | Bioregion.objects.filter(
                pk__in=self.instance.user_bioregions.values_list("pk", flat=True)
            )
        self.fields["user_bioregions"].queryset = visible_bioregions.distinct()

        # If editing, don't allow "invited_by" to be self
        if self.instance and self.instance.pk:
            self.fields["invited_by"].queryset = User.objects.exclude(pk=self.instance.pk)

        is_admin_editor = bool(
            self.current_user and (
                self.current_user.is_superuser or self.current_user.is_admin()
            )
        )

        if not is_admin_editor:
            self.fields.pop("invited_by", None)
            self.fields.pop("invite_role", None)

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

        primary_location = cleaned.get("primary_location")
        selected_locations = cleaned.get("user_locations")
        if primary_location and selected_locations is not None and primary_location not in selected_locations:
            cleaned["user_locations"] = selected_locations | Location.objects.filter(pk=primary_location.pk)

        alternate_deck = cleaned.get("alternate_deck") or ""
        cleaned["alternate_deck"] = slugify(alternate_deck)

        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        pwd = self.cleaned_data.get("password")

        if pwd:
            user.set_password(pwd)

        # Explicitly handle view_members, view_public, and ai_transcript_processing fields
        user.view_members = self.cleaned_data.get("view_members", user.view_members)
        user.view_public = self.cleaned_data.get("view_public", user.view_public)
        user.ai_transcript_processing = self.cleaned_data.get("ai_transcript_processing", user.ai_transcript_processing)

        if "invite_role" in self.cleaned_data:
            user.invite_role = self.cleaned_data.get("invite_role", user.invite_role)

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
