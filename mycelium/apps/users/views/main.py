from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.contenttypes.models import ContentType
from ..forms import LoginForm, RegisterForm, UserForm, UserPermissionForm
from apps.acl.utils import get_permitted_objects, get_permitted_object, is_permitted
from apps.utils import dump
from apps.utils.pagination import paginate_queryset
from apps.bookmarks.models import Bookmark
from django.db.models import Q
from django.utils import timezone
from django.urls import reverse
import base64
import io
import secrets
import qrcode

User = get_user_model()


def _can_invite_people(user):
    return bool(user and user.is_authenticated and user.can_invite())


def _can_approve_people(user):
    return bool(user and user.is_authenticated and user.can_approve_people())


def _can_approve_everyone(user):
    return bool(user and user.is_authenticated and (user.is_superuser or user.is_admin()))


def _registration_context(registration_mode, invite=None):
    if invite is None:
        return {
            "registration_mode": registration_mode,
            "invite": None,
            "inviter": None,
        }
    return {
        "registration_mode": registration_mode,
        "invite": invite,
        "inviter": invite.inviter,
    }


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


def register_view(request, token=None):
    from django.conf import settings
    from apps.users.models import UserInvite
    
    # Check registration mode
    registration_mode = settings.REGISTRATION_MODE

    invite = None
    if token:
        invite = UserInvite.objects.filter(token=token, status=UserInvite.STATUS_PENDING).select_related("inviter").first()
        if not invite:
            messages.error(request, "This invitation link is invalid or no longer active.")
            return redirect("register")
    
    if registration_mode == "closed" and invite is None:
        messages.error(request, "Self-registration is disabled. Please contact an administrator to create an account.")
        return redirect("login")
    
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            if invite:
                user.invited_by = invite.inviter
                user.invited_by_confirmed_at = None
            
            # Set approval status based on registration mode
            if registration_mode == "approval" or invite is not None:
                user.is_approved = False
                user.is_active = False  # Disable login until approved
            else:  # open mode
                user.is_approved = True
                user.is_active = True
            
            user.save()
            form.save_m2m()

            if invite and invite.bioregion:
                user.user_bioregions.add(invite.bioregion)

            if invite:
                invite.invited_user = user
                invite.status = UserInvite.STATUS_REGISTERED
                invite.save(update_fields=["invited_user", "status"])

                from apps.commons.models import CommonsApplication
                for commons in invite.requested_commons.all():
                    CommonsApplication.objects.get_or_create(
                        commons=commons,
                        applicant=user,
                        status=CommonsApplication.STATUS_PENDING,
                        defaults={"note": f"Requested at signup via invite from {invite.inviter.username}."},
                    )
            
            if registration_mode == "approval" or invite is not None:
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

    context = {"form": form}
    context.update(_registration_context(registration_mode, invite=invite))
    return render(request, "users/register.html", context)

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

    # Float bookmarked users to the top
    if request.user.is_authenticated:
        user_content_type = ContentType.objects.get_for_model(User)
        bookmarked_ids = set(
            Bookmark.objects.filter(
                user=request.user,
                content_type=user_content_type
            ).values_list('object_id', flat=True)
        )
        # Separate bookmarked from non-bookmarked
        users_list = list(users)
        bookmarked_users = [u for u in users_list if u.pk in bookmarked_ids]
        non_bookmarked_users = [u for u in users_list if u.pk not in bookmarked_ids]
        users_list = bookmarked_users + non_bookmarked_users
    else:
        users_list = list(users)

    # Pagination using helper function
    users_page, pagination_data = paginate_queryset(users_list, request, per_page=100)

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
        form = UserForm(request.POST, request.FILES, current_user=request.user)
        if form.is_valid():
            user = form.save()  # commit=True, so M2M will save
            messages.success(request, "Person created successfully.")
            return redirect("user_detail", pk=user.pk)
    else:
        form = UserForm(current_user=request.user)

    return render(request, "users/user_form.html", {"form": form, "user": None})


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def user_detail_view(request, pk):
    """View a user's details."""
    # Get the user to view
    user = get_permitted_object(request.user, "view", User, pk)
    from apps.stories.models import Story, StoryAttachment
    
    # Get all projects where the user has any role (member, owner, or admin)
    from apps.projects.models import Project
    from apps.locations.models import Location
    user_all_projects = Project.objects.filter(
        Q(members=user) | Q(owners=user) | Q(admins=user)
    ).distinct().order_by('title')

    permitted_locations = get_permitted_objects(request.user, "view", Location)
    user_location_ids = user.user_locations.values_list("pk", flat=True)
    if hasattr(permitted_locations, "filter"):
        user_locations = permitted_locations.filter(pk__in=user_location_ids).order_by("title")
        user_location_count = user_locations.count()
    else:
        permitted_location_ids = {loc.pk for loc in permitted_locations}
        user_locations = list(user.user_locations.filter(pk__in=permitted_location_ids).order_by("title"))
        user_location_count = len(user_locations)

    user_content_type = ContentType.objects.get_for_model(User)
    attached_story_ids = set(
        StoryAttachment.objects.filter(
            content_type=user_content_type,
            object_id=user.pk,
        ).values_list("story_id", flat=True)
    )

    permitted_stories = get_permitted_objects(request.user, "view", Story)
    if hasattr(permitted_stories, "filter"):
        user_stories = permitted_stories.filter(pk__in=attached_story_ids).order_by("-created_at")
        user_story_count = user_stories.count()
        user_stories_preview = user_stories[:3]
    else:
        user_stories = [s for s in permitted_stories if s.pk in attached_story_ids]
        user_stories.sort(key=lambda s: s.created_at, reverse=True)
        user_story_count = len(user_stories)
        user_stories_preview = user_stories[:3]
    
    is_self = request.user.pk == user.pk
    can_invite = is_self and _can_invite_people(request.user)
    invite_url = None
    invite_qr_b64 = None
    pending_invite_bioregion_title = None
    pending_invite_commons_titles = []
    invite_commons_choices = []

    if can_invite:
        from apps.users.models import UserInvite
        from apps.bioregions.models import Bioregion
        from apps.commons.utils import get_user_commons_queryset

        if request.user.is_superuser or request.user.is_admin():
            invite_bioregions = Bioregion.objects.all().order_by("title")
        else:
            invite_bioregions = request.user.user_bioregions.all().order_by("title")

        invite_commons_choices = get_user_commons_queryset(request.user).order_by("title").distinct()

        pending_invite = UserInvite.objects.filter(
            inviter=request.user,
            status=UserInvite.STATUS_PENDING,
        ).select_related("bioregion").prefetch_related("requested_commons").order_by("-created_at").first()
        if pending_invite:
            pending_invite_bioregion_title = pending_invite.bioregion.title if pending_invite.bioregion else None
            pending_invite_commons_titles = [c.title for c in pending_invite.requested_commons.all()]
            invite_url = request.build_absolute_uri(reverse("register_with_token", kwargs={"token": pending_invite.token}))
            qr = qrcode.QRCode(box_size=6, border=2)
            qr.add_data(invite_url)
            qr.make(fit=True)
            image = qr.make_image(fill_color="black", back_color="white")
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            invite_qr_b64 = base64.b64encode(buffer.getvalue()).decode("ascii")
    else:
        invite_bioregions = []

    return render(request, "users/user_detail.html", {
        "user": user,
        "user_all_projects": user_all_projects,
        "user_story_count": user_story_count,
        "user_stories_preview": user_stories_preview,
        "user_locations": user_locations,
        "user_location_count": user_location_count,
        "can_invite": can_invite,
        "invite_url": invite_url,
        "invite_qr_b64": invite_qr_b64,
        "invite_bioregions": invite_bioregions,
        "invite_commons_choices": invite_commons_choices,
        "pending_invite_bioregion_title": pending_invite_bioregion_title,
        "pending_invite_commons_titles": pending_invite_commons_titles,
    })


@login_required
def user_edit_view(request, pk):
    """Edit a user's details."""
    # Get the user to edit
    user = get_permitted_object(request.user, "change", User, pk)
    # If the request method is POST, update the user's details
    if request.method == "POST":
        # Update the user's details
        form = UserForm(request.POST, request.FILES, instance=user, current_user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Person updated successfully.")
            return redirect("user_detail", pk=user.pk)
    else:
        form = UserForm(instance=user, current_user=request.user)
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
    """View list of users pending approval (approvers and superusers)."""
    if not _can_approve_people(request.user):
        raise PermissionDenied
    
    pending_users = User.objects.filter(is_approved=False, is_active=False).select_related("invited_by").order_by('-date_joined')
    if not _can_approve_everyone(request.user):
        pending_users = pending_users.filter(invited_by=request.user)

    from apps.users.models import UserInvite
    pending_user_ids = list(pending_users.values_list("id", flat=True))
    invite_qs = UserInvite.objects.filter(invited_user_id__in=pending_user_ids).select_related("bioregion")
    pending_invites_by_user = {}
    for invite in invite_qs:
        pending_invites_by_user[invite.invited_user_id] = invite
    
    return render(request, "users/pending_users.html", {
        "pending_users": pending_users,
        "pending_invites_by_user": pending_invites_by_user,
    })


@login_required
def approve_user_view(request, pk):
    """Approve a pending user (approvers and superusers)."""
    if not _can_approve_people(request.user):
        raise PermissionDenied
    
    user = User.objects.get(pk=pk)
    if not _can_approve_everyone(request.user) and user.invited_by_id != request.user.id:
        raise PermissionDenied
    from apps.users.models import UserInvite
    
    if request.method == "POST":
        user.is_approved = True
        user.is_active = True
        if user.invited_by and user.invited_by_confirmed_at is None:
            user.invited_by_confirmed_at = timezone.now()
        user.save()

        invite = UserInvite.objects.filter(invited_user=user).order_by("-created_at").first()
        if invite:
            invite.status = UserInvite.STATUS_APPROVED
            invite.approved_by = request.user
            invite.approved_at = timezone.now()
            invite.save(update_fields=["status", "approved_by", "approved_at"])
        messages.success(request, f"Person {user.username} has been approved and can now log in.")
        return redirect("pending_users")
    
    return render(request, "users/approve_user.html", {"user_to_approve": user})


@login_required
def reject_user_view(request, pk):
    """Reject a pending user (approvers and superusers)."""
    if not _can_approve_people(request.user):
        raise PermissionDenied
    
    user = User.objects.get(pk=pk)
    if not _can_approve_everyone(request.user) and user.invited_by_id != request.user.id:
        raise PermissionDenied
    
    if request.method == "POST":
        username = user.username
        from apps.users.models import UserInvite
        UserInvite.objects.filter(invited_user=user, status=UserInvite.STATUS_REGISTERED).update(
            status=UserInvite.STATUS_REVOKED,
            approved_by=request.user,
            approved_at=timezone.now(),
        )
        user.delete()
        messages.success(request, f"Person registration for {username} has been rejected and deleted.")
        return redirect("pending_users")
    
    return render(request, "users/reject_user.html", {"user_to_reject": user})


@login_required
def create_invite_view(request):
    from apps.users.models import UserInvite
    from apps.bioregions.models import Bioregion

    if not _can_invite_people(request.user):
        raise PermissionDenied

    if request.method != "POST":
        return redirect("user_detail", pk=request.user.pk)

    bioregion_id = (request.POST.get("bioregion") or "").strip()
    if not bioregion_id:
        messages.error(request, "Select a bioregion for the invitation.")
        return redirect("user_detail", pk=request.user.pk)

    try:
        bioregion = Bioregion.objects.get(pk=bioregion_id)
    except Bioregion.DoesNotExist:
        messages.error(request, "Selected bioregion was not found.")
        return redirect("user_detail", pk=request.user.pk)

    if not (request.user.is_superuser or request.user.is_admin()):
        if not request.user.user_bioregions.filter(pk=bioregion.pk).exists():
            messages.error(request, "You can only create invites for your own bioregions.")
            return redirect("user_detail", pk=request.user.pk)

    token = secrets.token_urlsafe(24)
    invite = UserInvite.objects.create(
        token=token,
        inviter=request.user,
        bioregion=bioregion,
        invited_email=(request.POST.get("invited_email") or "").strip() or None,
    )

    from apps.commons.utils import get_user_commons_queryset
    requested_commons_ids = request.POST.getlist("commons")
    if requested_commons_ids:
        allowed_commons = get_user_commons_queryset(request.user).filter(pk__in=requested_commons_ids)
        invite.requested_commons.set(allowed_commons)

    invite_url = request.build_absolute_uri(reverse("register_with_token", kwargs={"token": invite.token}))
    messages.success(request, f"Invite created for bioregion '{bioregion.title}'. Share this link: {invite_url}")
    return redirect("user_detail", pk=request.user.pk)
