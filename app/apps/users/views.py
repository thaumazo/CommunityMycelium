from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserForm

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
            messages.error(request, "Invalid credentials")
            return render(request, "users/login.html")

    return render(request, "users/login.html")


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, "users/register.html")

        User.objects.create_user(username=username, password=password, email=email)
        messages.success(
            request, "Registration successful! Please log in with your new account."
        )
        return redirect("login")
    return render(request, "users/register.html")


@login_required
def user_list_view(request):
    users = User.objects.all()
    return render(request, "users/user_list.html", {"users": users})


@login_required
def user_create_view(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("user_list")
    else:
        form = UserForm()
    return render(
        request, "users/user_form.html", {"form": form, "title": "Create User"}
    )


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def user_detail_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    return render(request, "users/user_detail.html", {"user": user})


@login_required
def user_edit_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "User updated successfully.")
            return redirect("user_detail", pk=user.pk)
    else:
        form = UserForm(instance=user)
    return render(request, "users/user_form.html", {"form": form, "title": "Edit User"})


@login_required
def user_delete_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        user.delete()
        messages.success(request, "User deleted successfully.")
        return redirect("user_list")
    return render(request, "users/user_confirm_delete.html", {"user": user})
