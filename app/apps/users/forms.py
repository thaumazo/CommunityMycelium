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
        required=False
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(), 
        label="Confirm Password",
        required=False
    )
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=True,
        label="User Type"
    )

    class Meta:
        model = User
        fields = ["username", "email", "password", "group"]
        widgets = {
            "username": forms.TextInput(),
            "email": forms.EmailInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # If editing an existing user, set the initial group
            user_groups = self.instance.groups.all()
            if user_groups.exists():
                self.fields['group'].initial = user_groups.first()

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get("password"):
            user.set_password(self.cleaned_data["password"])
        
        if commit:
            user.save()
            # Update user's group
            user.groups.clear()
            user.groups.add(self.cleaned_data["group"])
            
        return user
