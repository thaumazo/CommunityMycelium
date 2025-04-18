from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

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


def logout_view(request):
    logout(request)
    return redirect("login")
