from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .forms import LoginForm, RegisterForm, UserForm, UserPermissionForm
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


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Registration successful! Please log in with your new account."
            )
            return redirect("login")
    else:
        form = UserForm()

    return render(request, "users/register.html", {"form": form})


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
                # Clear existing groups and set the new ones
                user.groups.clear()
                if form.cleaned_data["groups"]:
                    user.groups.add(*form.cleaned_data["groups"])
                messages.success(request, "User roles updated successfully.")
                return redirect("user_detail", pk=user.pk)
        else:
            form = UserPermissionForm(user=user)

        return render(
            request,
            "users/user_permission_form.html",
            {"user": user, "form": form, "title": "Edit User Roles"},
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
