from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from .forms import LoginForm, RegisterForm, UserForm, UserPermissionForm
from .models import EmailVerification
from apps.acl.utils import get_permitted_objects, get_permitted_object

User = get_user_model()


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get("next", "home")
                return redirect(next_url)
    else:
        form = LoginForm()

    return render(request, "users/login.html", {"form": form})


def send_verification_email(user, verification):
    verification_url = settings.SITE_URL + reverse('verify_email', args=[verification.token])
    context = {
        'verification_url': verification_url,
        'expiry_days': settings.EMAIL_VERIFICATION_EXPIRY_DAYS
    }
    html_message = render_to_string('users/email/verification_email.html', context)
    
    send_mail(
        subject='Verify your email address',
        message='Please verify your email address by clicking the link in the email.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message
    )


def register_view(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # User is inactive until email is verified
            user.save()
            
            # Create email verification
            verification = EmailVerification.create_verification(user)
            
            # Send verification email
            send_verification_email(user, verification)
            
            messages.success(
                request, 
                "Registration successful! Please check your email to verify your account."
            )
            return redirect("login")
    else:
        form = UserForm()

    return render(request, "users/register.html", {"form": form})


def verify_email_view(request, token):
    try:
        verification = EmailVerification.objects.get(token=token)
        if verification.verify():
            messages.success(request, "Email verified successfully! You can now log in.")
        else:
            messages.error(request, "Verification link has expired. Please request a new one.")
    except EmailVerification.DoesNotExist:
        messages.error(request, "Invalid verification link.")
    
    return redirect("login")


@login_required
def user_list_view(request):
    """View a list of all users."""
    users = get_permitted_objects(request.user, "view", User)
    return render(request, "users/user_list.html", {"users": users})


@login_required
def user_create_view(request):
    """Create a new user."""
    # If the request method is POST, create a new user
    if request.method == "POST":
        # Create a new user form
        form = RegisterForm(request.POST)
        # If the form is valid, save the user
        if form.is_valid():
            # Save the user
            form.save()
            # Add a success message
            messages.success(request, "User created successfully.")
            # Redirect to the user list
            return redirect("user_list")
    else:
        # Create a new user form
        form = RegisterForm()
    # Render the user form
    return render(
        request, "users/user_form.html", {"form": form, "title": "Create User"}
    )


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def user_detail_view(request, pk):
    """View a user's details."""
    # Get the user to view
    user = get_permitted_object(request.user, "view", User, pk)
    # Render the user details
    return render(request, "users/user_detail.html", {"user": user})


@login_required
def user_edit_view(request, pk):
    """Edit a user's details."""
    # Get the user to edit
    user = get_permitted_object(request.user, "change", User, pk)
    # If the request method is POST, update the user's details
    if request.method == "POST":
        # Update the user's details
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "User updated successfully.")
            return redirect("user_detail", pk=user.pk)
    else:
        form = UserForm(instance=user)
    # Render the user form
    return render(
        request,
        "users/user_form.html",
        {"form": form, "title": "Edit User", "user": user},
    )


@login_required
def user_permission_edit_view(request, pk):
    """Edit a user's permissions."""
    if request.user.is_admin():
        user = User.objects.get(pk=pk)
        if request.method == "POST":
            form = UserPermissionForm(request.POST, user=user)
            if form.is_valid():
                # Clear existing groups and set the new one
                user.groups.clear()
                if form.cleaned_data["groups"]:
                    user.groups.add(form.cleaned_data["groups"])
                messages.success(request, "User role updated successfully.")
                return redirect("user_detail", pk=user.pk)
        else:
            form = UserPermissionForm(user=user)

        return render(
            request,
            "users/user_permission_form.html",
            {"user": user, "form": form, "title": "Edit User Role"},
        )
    else:
        raise PermissionDenied


@login_required
def user_delete_view(request, pk):
    """Delete a user."""
    # Get the user to delete
    user = get_permitted_object(request.user, "delete", User, pk)
    # If the request method is POST, delete the user
    if request.method == "POST":
        # Delete the user
        user.delete()
        # Add a success message
        messages.success(request, "User deleted successfully.")
        # Redirect to the user list
        return redirect("user_list")
    # Render the user confirmation delete page
    return render(request, "users/user_confirm_delete.html", {"user": user})
