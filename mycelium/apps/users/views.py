from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .forms import LoginForm, RegisterForm, UserForm, UserPermissionForm
from apps.acl.utils import get_permitted_objects, get_permitted_object, is_permitted
from apps.utils import dump
from apps.utils.pagination import paginate_queryset
from django.db.models import Q

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
                next_url = request.GET.get("next", "core:home")
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
        # ✅ was: form = UserForm()
        form = RegisterForm()

    return render(request, "users/register.html", {"form": form})

@login_required
def user_list_view(request):
    """View a list of all users."""
    # Get users based on current permissions
    permitted_users = get_permitted_objects(request.user, "view", User)

    # Ensure permitted_users contains a list of IDs
    permitted_users = User.objects.filter(pk__in=[user.pk for user in permitted_users])

    # Include users with view_members or view_public set to True
    additional_users = User.objects.filter(
        Q(view_members=True) | Q(view_public=True)
    )

    # Combine both querysets and ensure no duplicates
    users = permitted_users | additional_users
    users = users.distinct()

    # Pagination using helper function
    users_page, pagination_data = paginate_queryset(users, request, per_page=100)

    return render(request, "users/user_list.html", {
        "users": users_page,
        "pagination": pagination_data,
    })


@login_required
def user_create_view(request):
    """Create a new user."""
    if not is_permitted(request.user, "add", "users.user"):
        raise PermissionDenied

    if request.method == "POST":
        # ✅ was RegisterForm
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()  # commit=True, so M2M will save
            messages.success(request, "User created successfully.")
            return redirect("user_detail", pk=user.pk)
    else:
        form = UserForm()

    return render(request, "users/user_form.html", {"form": form, "user": None})


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
        form = UserForm(request.POST, request.FILES, instance=user)
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
        {"form": form, "user": user},
    )


@login_required
def user_permission_edit_view(request, pk):
    """Edit a user's permissions."""
    if request.user.is_admin():
        user = User.objects.get(pk=pk)
    else:
        raise PermissionDenied

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
        {"user": user, "form": form},
    )


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


def user_character_view(request, pk):
    """View a user's character sheet. Public if user has view_public=True."""
    from apps.stories.models import Story, StoryAttachment
    from django.contrib.contenttypes.models import ContentType
    
    user_to_view = None
    
    if request.user.is_authenticated:
        # Authenticated users: try permission check first, then fallback to visibility flags
        try:
            user_to_view = get_permitted_object(request.user, "view", User, pk)
        except (PermissionDenied, User.DoesNotExist):
            user_to_view = User.objects.filter(
                pk=pk
            ).filter(
                Q(view_members=True) | Q(view_public=True)
            ).first()
    else:
        # Unauthenticated users: only see public profiles
        user_to_view = User.objects.filter(pk=pk, view_public=True).first()

    if not user_to_view:
        raise PermissionDenied

    # Get stories attached to this user's character elements
    story_attachments = {}
    
    # Get all facets, roles, and maladaptives for this user
    facets = user_to_view.user_metacrisis_facets.all()
    roles = user_to_view.user_socialroles.all()
    maladaptives = user_to_view.user_maladaptives.all()
    
    # For each element, get attached stories that user can view
    for facet in facets:
        ct = ContentType.objects.get_for_model(facet)
        attachments = StoryAttachment.objects.filter(
            content_type=ct,
            object_id=facet.id
        ).select_related('story', 'story__created_by')
        
        # Filter by visibility
        visible_stories = []
        for attachment in attachments:
            story = attachment.story
            if request.user.is_authenticated:
                if (story.created_by == request.user or 
                    story.view_members or 
                    story.view_public or 
                    request.user.is_superuser):
                    visible_stories.append(attachment)
            else:
                if story.view_public:
                    visible_stories.append(attachment)
        
        if visible_stories:
            story_attachments[f'metacrisis_facet_{facet.id}'] = visible_stories
    
    for role in roles:
        ct = ContentType.objects.get_for_model(role)
        attachments = StoryAttachment.objects.filter(
            content_type=ct,
            object_id=role.id
        ).select_related('story', 'story__created_by')
        
        visible_stories = []
        for attachment in attachments:
            story = attachment.story
            if request.user.is_authenticated:
                if (story.created_by == request.user or 
                    story.view_members or 
                    story.view_public or 
                    request.user.is_superuser):
                    visible_stories.append(attachment)
            else:
                if story.view_public:
                    visible_stories.append(attachment)
        
        if visible_stories:
            story_attachments[f'socialrole_{role.id}'] = visible_stories
    
    for maladaptive in maladaptives:
        ct = ContentType.objects.get_for_model(maladaptive)
        attachments = StoryAttachment.objects.filter(
            content_type=ct,
            object_id=maladaptive.id
        ).select_related('story', 'story__created_by')
        
        visible_stories = []
        for attachment in attachments:
            story = attachment.story
            if request.user.is_authenticated:
                if (story.created_by == request.user or 
                    story.view_members or 
                    story.view_public or 
                    request.user.is_superuser):
                    visible_stories.append(attachment)
            else:
                if story.view_public:
                    visible_stories.append(attachment)
        
        if visible_stories:
            story_attachments[f'maladaptive_{maladaptive.id}'] = visible_stories

    return render(request, "users/user_character.html", {
        "user": user_to_view,
        "story_attachments": story_attachments,
    })
