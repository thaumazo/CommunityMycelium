from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from ..forms import LoginForm, RegisterForm, UserForm, UserPermissionForm
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
    from django.conf import settings
    
    # Check registration mode
    registration_mode = settings.REGISTRATION_MODE
    
    if registration_mode == "closed":
        messages.error(request, "Self-registration is disabled. Please contact an administrator to create an account.")
        return redirect("login")
    
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            # Set approval status based on registration mode
            if registration_mode == "approval":
                user.is_approved = False
                user.is_active = False  # Disable login until approved
            else:  # open mode
                user.is_approved = True
                user.is_active = True
            
            user.save()
            form.save_m2m()
            
            if registration_mode == "approval":
                messages.success(
                    request, "Registration submitted! Your account is pending approval by an administrator."
                )
            else:
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
    users = users.distinct().order_by('full_name')

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
            messages.success(request, "Person created successfully.")
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
    
    # Get all projects where the user has any role (member, owner, or admin)
    from apps.projects.models import Project
    user_all_projects = Project.objects.filter(
        Q(members=user) | Q(owners=user) | Q(admins=user)
    ).distinct().order_by('title')
    
    # Render the user details
    return render(request, "users/user_detail.html", {
        "user": user,
        "user_all_projects": user_all_projects
    })


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
            messages.success(request, "Person updated successfully.")
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
            messages.success(request, "Person roles updated successfully.")
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
        messages.success(request, "Person deleted successfully.")
        # Redirect to the user list
        return redirect("user_list")

    # Render the user confirmation delete page
    return render(request, "users/user_confirm_delete.html", {"user": user})


def user_character_view(request, pk):
    """View a user's character sheet. Public if user has view_public=True."""
    from apps.stories.models import Story, StoryAttachment
    from django.contrib.contenttypes.models import ContentType
    from apps.socialroles.models import UserSocialrole
    from apps.metacrisis_facets.models import UserMetacrisisFacet
    from apps.maladaptives.models import UserMaladaptive
    
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

    # Get through model instances (user-specific relationships)
    user_socialroles = UserSocialrole.objects.filter(user=user_to_view).select_related('socialrole')
    user_metacrisis_facets = UserMetacrisisFacet.objects.filter(user=user_to_view).select_related('metacrisis_facet')
    user_maladaptives = UserMaladaptive.objects.filter(user=user_to_view).select_related('maladaptive')
    
    # Get stories attached to this user's character elements
    story_attachments = {}
    
    # Helper function to filter stories by visibility
    def get_visible_attachments(attachments):
        visible = []
        for attachment in attachments:
            story = attachment.story
            if request.user.is_authenticated:
                if (story.created_by == request.user or 
                    story.view_members or 
                    story.view_public or 
                    request.user.is_superuser):
                    visible.append(attachment)
            else:
                if story.view_public:
                    visible.append(attachment)
        return visible
    
    # Get stories for social roles (attached to UserSocialrole instances)
    for user_socialrole in user_socialroles:
        ct = ContentType.objects.get_for_model(user_socialrole)
        attachments = StoryAttachment.objects.filter(
            content_type=ct,
            object_id=user_socialrole.id
        ).select_related('story', 'story__created_by')
        
        visible_stories = get_visible_attachments(attachments)
        if visible_stories:
            # Key by socialrole id for template compatibility
            story_attachments[f'socialrole_{user_socialrole.socialrole.id}'] = visible_stories
    
    # Get stories for metacrisis facets (attached to UserMetacrisisFacet instances)
    for user_facet in user_metacrisis_facets:
        ct = ContentType.objects.get_for_model(user_facet)
        attachments = StoryAttachment.objects.filter(
            content_type=ct,
            object_id=user_facet.id
        ).select_related('story', 'story__created_by')
        
        visible_stories = get_visible_attachments(attachments)
        if visible_stories:
            story_attachments[f'metacrisis_facet_{user_facet.metacrisis_facet.id}'] = visible_stories
    
    # Get stories for maladaptives (attached to UserMaladaptive instances)
    for user_maladaptive in user_maladaptives:
        ct = ContentType.objects.get_for_model(user_maladaptive)
        attachments = StoryAttachment.objects.filter(
            content_type=ct,
            object_id=user_maladaptive.id
        ).select_related('story', 'story__created_by')
        
        visible_stories = get_visible_attachments(attachments)
        if visible_stories:
            story_attachments[f'maladaptive_{user_maladaptive.maladaptive.id}'] = visible_stories

    return render(request, "users/user_character.html", {
        "user": user_to_view,
        "story_attachments": story_attachments,
        "user_socialroles": user_socialroles,
        "user_metacrisis_facets": user_metacrisis_facets,
        "user_maladaptives": user_maladaptives,
    })


@login_required
def pending_users_view(request):
    """View list of users pending approval (superuser only)."""
    if not request.user.is_superuser:
        raise PermissionDenied
    
    pending_users = User.objects.filter(is_approved=False, is_active=False).order_by('-date_joined')
    
    return render(request, "users/pending_users.html", {
        "pending_users": pending_users,
    })


@login_required
def approve_user_view(request, pk):
    """Approve a pending user (superuser only)."""
    if not request.user.is_superuser:
        raise PermissionDenied
    
    user = User.objects.get(pk=pk)
    
    if request.method == "POST":
        user.is_approved = True
        user.is_active = True
        user.save()
        messages.success(request, f"Person {user.username} has been approved and can now log in.")
        return redirect("pending_users")
    
    return render(request, "users/approve_user.html", {"user_to_approve": user})


@login_required
def reject_user_view(request, pk):
    """Reject a pending user (superuser only)."""
    if not request.user.is_superuser:
        raise PermissionDenied
    
    user = User.objects.get(pk=pk)
    
    if request.method == "POST":
        username = user.username
        user.delete()
        messages.success(request, f"Person registration for {username} has been rejected and deleted.")
        return redirect("pending_users")
    
    return render(request, "users/reject_user.html", {"user_to_reject": user})
