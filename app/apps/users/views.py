from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from .models import UserProfile
from .forms import UserForm, UserProfileForm
from django.core.exceptions import PermissionDenied

User = get_user_model()


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get("next", "home")
            return redirect(next_url)
        else:
            return render(request, "users/login.html", {"error": "Invalid credentials"})
    return render(request, "users/login.html")


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")
        if User.objects.filter(username=username).exists():
            return render(
                request, "users/register.html", {"error": "Username already exists"}
            )
        user = User.objects.create_user(
            username=username, password=password, email=email
        )
        # Create profile with viewer role
        UserProfile.objects.create(user=user, is_viewer=True)
        messages.success(
            request, "Registration successful! Please log in with your new account."
        )
        return redirect("login")
    return render(request, "users/register.html")


@login_required
@permission_required("users.view_user", raise_exception=True)
def user_list_view(request):
    users = User.objects.all().order_by("username")
    return render(request, "users/user_list.html", {"users": users})


@login_required
@permission_required("users.view_user", raise_exception=True)
def user_detail_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    profile = user.profile
    return render(request, "users/user_detail.html", {"user": user, "profile": profile})


@login_required
@permission_required("users.add_user", raise_exception=True)
def user_create_view(request):
    if request.method == "POST":
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            # Create the profile with the form data
            profile = UserProfile.objects.create(
                user=user,
                is_viewer=profile_form.cleaned_data["is_viewer"],
                is_editor=profile_form.cleaned_data["is_editor"],
                is_admin=profile_form.cleaned_data["is_admin"],
            )
            messages.success(request, "User created successfully!")
            return redirect("user_list")
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(
        request,
        "users/user_form.html",
        {"user_form": user_form, "profile_form": profile_form, "title": "Create User"},
    )


@login_required
def user_edit_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    profile = user.profile

    # Allow users to edit their own profile or admins to edit any profile
    if not (request.user.pk == user.pk or request.user.profile.is_admin):
        raise PermissionDenied("You don't have permission to edit this user's profile.")

    if request.method == "POST":
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            # Only allow admins to change role permissions
            if not request.user.profile.is_admin:
                profile_form.instance.is_viewer = profile.is_viewer
                profile_form.instance.is_editor = profile.is_editor
                profile_form.instance.is_admin = profile.is_admin
            profile_form.save()
            messages.success(request, "User updated successfully!")
            return redirect("user_list")
    else:
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=profile)

    return render(
        request,
        "users/user_form.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
            "title": "Edit User",
            "user": user,
        },
    )


@login_required
@permission_required("users.delete_user", raise_exception=True)
def user_delete_view(request, pk):
    user = get_object_or_404(User, pk=pk)

    if request.method == "POST":
        user.delete()
        messages.success(request, "User deleted successfully!")
        return redirect("user_list")

    return render(request, "users/user_confirm_delete.html", {"user": user})


def logout_view(request):
    logout(request)
    return redirect("login")
