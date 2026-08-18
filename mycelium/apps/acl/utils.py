from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied
from django.http import Http404
from .models import ObjectPermission, ModelPermission
from apps.utils.dump import dump
from apps.users.models import User


def is_permitted(user, action, obj_or_string):
    """
    Check if a user has permission to perform `action` on `obj`.
    
    Permission hierarchy:
    1. Self-permission (user accessing their own User object)
    2. Ownership (user created the object)
    3. Public access rules (bioregions, related challenges)
    4. Model-level permission via groups (Django's built-in)
    5. Model-level permission via ModelPermission (individual user)
    6. Object-level permission via ObjectPermission (specific object)
    """
    # If the object is a string, it's a model name
    if isinstance(obj_or_string, str):
        # Create a empty object instance of the model
        obj = ContentType.objects.get(
            app_label=obj_or_string.split(".")[0], model=obj_or_string.split(".")[1]
        ).model_class()()
    else:
        obj = obj_or_string

    # Public access rules for bioregions
    from apps.bioregions.models import Bioregion
    from apps.challenges.models import Challenge
    from apps.communities.models import Community
    from apps.projects.models import Project
    from apps.locations.models import Location
    
    # Handle anonymous users - check public visibility rules only
    if not user.is_authenticated:
        from apps.stories.models import Story
        # Anonymous users can only view objects with view_public=True
        if isinstance(obj, User) and action == "view" and hasattr(obj, 'view_public'):
            return obj.view_public
        if isinstance(obj, Community) and action == "view" and hasattr(obj, 'view_public'):
            return obj.view_public
        if isinstance(obj, Project) and action == "view" and hasattr(obj, 'view_public'):
            return obj.view_public
        if isinstance(obj, Location) and action == "view" and hasattr(obj, 'view_public'):
            return obj.view_public
        if isinstance(obj, Story) and action == "view" and hasattr(obj, 'view_public'):
            return obj.view_public
        # Anonymous users cannot perform any other actions
        return False

    # Universal ownership rule: creators can always view/edit their own items,
    # and owners/admins/members can always view/edit items where those roles exist.
    # This takes precedence over any model-specific visibility gating below
    # (e.g. pending community notes), matching the requirement that owners of
    # content are never locked out of their own items.
    if getattr(obj, "pk", None):
        if action in ("view", "change") and hasattr(obj, "created_by") and obj.created_by == user:
            return True
        if action in ("view", "change"):
            for relation_name in ("owners", "admins"):
                relation = getattr(obj, relation_name, None)
                if relation is not None and hasattr(relation, "all") and user in relation.all():
                    return True
        if action == "view":
            relation = getattr(obj, "members", None)
            if relation is not None and hasattr(relation, "all") and user in relation.all():
                return True

    if isinstance(obj, Bioregion) and action == "view":
        # Any authenticated user can view bioregions
        if user.is_authenticated:
            return True
    
    if isinstance(obj, Challenge) and action == "view":
        # Any authenticated user can view challenges that have a related bioregion
        if user.is_authenticated and obj.related_bioregion:
            return True
    
    # Allow any authenticated user to create projects
    if isinstance(obj, Project) and action == "add":
        if user.is_authenticated:
            return True

    # Allow any authenticated user to create locations
    if isinstance(obj, Location) and action == "add":
        if user.is_authenticated:
            return True

    # If the object is a user, and it's the current user
    if isinstance(obj, User) and obj == user:
        return True
    
    # Visibility rules for users
    if isinstance(obj, User) and action == "view":
        # Superusers can see everyone
        if user.is_superuser:
            return True
        # Authenticated members can see users with view_members=True
        if user.is_authenticated and obj.view_members:
            return True
        # Public users can see users with view_public=True
        if obj.view_public:
            return True
    
    # Visibility rules for communities
    if isinstance(obj, Community) and action == "view":
        # Creator can always see their own community
        if hasattr(obj, "created_by") and obj.created_by == user:
            return True
        # Superusers can see all communities
        if user.is_superuser:
            return True
        # Authenticated members can see communities with view_members=True
        if user.is_authenticated and obj.view_members:
            return True
        # Public users can see communities with view_public=True
        if obj.view_public:
            return True
    
    # Visibility rules for projects
    if isinstance(obj, Project) and action == "view":
        # Creator can always see their own project
        if hasattr(obj, "created_by") and obj.created_by == user:
            return True
        # Project admins and owners can always view the project
        if hasattr(obj, "pk") and obj.pk:
            if user in obj.admins.all() or user in obj.owners.all():
                return True
        # Superusers can see all projects
        if user.is_superuser:
            return True
        # Authenticated members can see projects with view_members=True
        if user.is_authenticated and obj.view_members:
            return True
        # Public users can see projects with view_public=True
        if obj.view_public:
            return True
    
    # Edit permissions for projects
    if isinstance(obj, Project) and action == "change":
        # Creator can always edit their own project
        if hasattr(obj, "created_by") and obj.created_by == user:
            return True
        # Project admins and owners can always edit the project
        if hasattr(obj, "pk") and obj.pk:
            if user in obj.admins.all() or user in obj.owners.all():
                return True
        # Superusers can edit all projects
        if user.is_superuser:
            return True
    
    # Delete permissions for projects
    if isinstance(obj, Project) and action == "delete":
        # Creator can always delete their own project
        if hasattr(obj, "created_by") and obj.created_by == user:
            return True
        # Project admins and owners can always delete the project
        if hasattr(obj, "pk") and obj.pk:
            if user in obj.admins.all() or user in obj.owners.all():
                return True
        # Superusers can delete all projects
        if user.is_superuser:
            return True
    
    # Permissions for ProjectCapitalIn and ProjectCapitalOut
    from apps.projects.models import ProjectCapitalIn, ProjectCapitalOut
    if isinstance(obj, (ProjectCapitalIn, ProjectCapitalOut)):
        # Project admins and owners can view, change, and delete project capitals
        if hasattr(obj, "project") and obj.project:
            if user in obj.project.admins.all() or user in obj.project.owners.all():
                return True
        # Creator can manage their project capitals
        if hasattr(obj, "created_by") and obj.created_by == user:
            return True
        # Superusers can do everything
        if user.is_superuser:
            return True

    # Visibility rules for locations
    if isinstance(obj, Location) and action == "view":
        if hasattr(obj, "created_by") and obj.created_by == user:
            return True
        if user.is_superuser:
            return True
        if user.is_authenticated and obj.view_members:
            return True
        if obj.view_public:
            return True
    
    # Visibility rules for stories
    from apps.stories.models import Story
    if isinstance(obj, Story) and action == "view":
        # Community notes remain private to project admins/owners until promoted
        if getattr(obj, "is_community_note", False) and getattr(obj, "community_note_status", "") != Story.COMMUNITY_NOTE_PROMOTED:
            if user.is_superuser:
                return True

            if hasattr(obj, "pk") and obj.pk and user.is_authenticated:
                from apps.stories.models import StoryAttachment
                from apps.projects.models import ProjectCapitalIn, ProjectCapitalOut

                attachments = StoryAttachment.objects.filter(story=obj).select_related('content_type')
                ct_capital_in = ContentType.objects.get_for_model(ProjectCapitalIn)
                ct_capital_out = ContentType.objects.get_for_model(ProjectCapitalOut)

                for attachment in attachments:
                    if attachment.content_type == ct_capital_in:
                        try:
                            project_capital = ProjectCapitalIn.objects.get(pk=attachment.object_id)
                            project = project_capital.project
                            if user in project.admins.all() or user in project.owners.all():
                                return True
                        except ProjectCapitalIn.DoesNotExist:
                            pass

                    if attachment.content_type == ct_capital_out:
                        try:
                            project_capital = ProjectCapitalOut.objects.get(pk=attachment.object_id)
                            project = project_capital.project
                            if user in project.admins.all() or user in project.owners.all():
                                return True
                        except ProjectCapitalOut.DoesNotExist:
                            pass

            return False

        # Creator can always see their own story
        if hasattr(obj, "created_by") and obj.created_by == user:
            return True
        # Superusers can see all stories
        if user.is_superuser:
            return True
        # Check if story is attached to a project capital and user is admin/owner of that project
        if hasattr(obj, "pk") and obj.pk and user.is_authenticated:
            from apps.stories.models import StoryAttachment
            from apps.projects.models import ProjectCapitalIn, ProjectCapitalOut
            
            # Get all attachments for this story
            attachments = StoryAttachment.objects.filter(story=obj).select_related('content_type')
            
            for attachment in attachments:
                # Check if attached to ProjectCapitalIn
                ct_capital_in = ContentType.objects.get_for_model(ProjectCapitalIn)
                if attachment.content_type == ct_capital_in:
                    try:
                        project_capital = ProjectCapitalIn.objects.get(pk=attachment.object_id)
                        project = project_capital.project
                        if user in project.admins.all() or user in project.owners.all():
                            return True
                    except ProjectCapitalIn.DoesNotExist:
                        pass
                
                # Check if attached to ProjectCapitalOut
                ct_capital_out = ContentType.objects.get_for_model(ProjectCapitalOut)
                if attachment.content_type == ct_capital_out:
                    try:
                        project_capital = ProjectCapitalOut.objects.get(pk=attachment.object_id)
                        project = project_capital.project
                        if user in project.admins.all() or user in project.owners.all():
                            return True
                    except ProjectCapitalOut.DoesNotExist:
                        pass
        # Authenticated members can see stories with view_members=True
        if user.is_authenticated and obj.view_members:
            return True
        # Public users can see stories with view_public=True
        if obj.view_public:
            return True
    
    # Edit permissions for stories
    if isinstance(obj, Story) and action == "change":
        # Creator can always edit their own story
        if hasattr(obj, "created_by") and obj.created_by == user:
            return True
        # Superusers can edit all stories
        if user.is_superuser:
            return True
        # Check if story is attached to a project capital and user is admin/owner of that project
        if hasattr(obj, "pk") and obj.pk:
            from apps.stories.models import StoryAttachment
            from apps.projects.models import ProjectCapitalIn, ProjectCapitalOut
            
            # Get all attachments for this story
            attachments = StoryAttachment.objects.filter(story=obj).select_related('content_type')
            
            for attachment in attachments:
                # Check if attached to ProjectCapitalIn
                ct_capital_in = ContentType.objects.get_for_model(ProjectCapitalIn)
                if attachment.content_type == ct_capital_in:
                    try:
                        project_capital = ProjectCapitalIn.objects.get(pk=attachment.object_id)
                        project = project_capital.project
                        if user in project.admins.all() or user in project.owners.all():
                            return True
                    except ProjectCapitalIn.DoesNotExist:
                        pass
                
                # Check if attached to ProjectCapitalOut
                ct_capital_out = ContentType.objects.get_for_model(ProjectCapitalOut)
                if attachment.content_type == ct_capital_out:
                    try:
                        project_capital = ProjectCapitalOut.objects.get(pk=attachment.object_id)
                        project = project_capital.project
                        if user in project.admins.all() or user in project.owners.all():
                            return True
                    except ProjectCapitalOut.DoesNotExist:
                        pass
    
    # Delete permissions for stories
    if isinstance(obj, Story) and action == "delete":
        # Creator can always delete their own story
        if hasattr(obj, "created_by") and obj.created_by == user:
            return True
        # Superusers can delete all stories
        if user.is_superuser:
            return True
        # Check if story is attached to a project capital and user is admin/owner of that project
        if hasattr(obj, "pk") and obj.pk:
            from apps.stories.models import StoryAttachment
            from apps.projects.models import ProjectCapitalIn, ProjectCapitalOut
            
            # Get all attachments for this story
            attachments = StoryAttachment.objects.filter(story=obj).select_related('content_type')
            
            for attachment in attachments:
                # Check if attached to ProjectCapitalIn
                ct_capital_in = ContentType.objects.get_for_model(ProjectCapitalIn)
                if attachment.content_type == ct_capital_in:
                    try:
                        project_capital = ProjectCapitalIn.objects.get(pk=attachment.object_id)
                        project = project_capital.project
                        if user in project.admins.all() or user in project.owners.all():
                            return True
                    except ProjectCapitalIn.DoesNotExist:
                        pass
                
                # Check if attached to ProjectCapitalOut
                ct_capital_out = ContentType.objects.get_for_model(ProjectCapitalOut)
                if attachment.content_type == ct_capital_out:
                    try:
                        project_capital = ProjectCapitalOut.objects.get(pk=attachment.object_id)
                        project = project_capital.project
                        if user in project.admins.all() or user in project.owners.all():
                            return True
                    except ProjectCapitalOut.DoesNotExist:
                        pass
    
    # ACL rules for through models (user-specific relationships)
    from apps.socialroles.models import UserSocialrole
    from apps.metacrisis_facets.models import UserMetacrisisFacet
    from apps.maladaptives.models import UserMaladaptive
    
    # Users can change their own user-specific relationship instances
    if isinstance(obj, (UserSocialrole, UserMetacrisisFacet, UserMaladaptive)):
        # User owns this relationship
        if hasattr(obj, "user") and obj.user == user:
            return True
        # Superusers can change any relationship
        if user.is_superuser:
            return True
    
    # First, if the object is owned by the user, they can always perform the action
    if hasattr(obj, "created_by") and obj.created_by == user:
        return True

    # Check if user has model-level permission through their groups
    model_permission = f"{action}_{obj._meta.model_name}"
    if user.has_perm(f"{obj._meta.app_label}.{model_permission}"):
        return True

    # Check if user has model-level permission via ModelPermission
    content_type = ContentType.objects.get_for_model(obj)
    if ModelPermission.objects.filter(
        user=user, action=action, content_type=content_type
    ).exists():
        return True

    # Finally, check object-level permissions
    return ObjectPermission.objects.filter(
        user=user, action=action, content_type=content_type, object_id=obj.pk
    ).exists()


def grant_model_permission(user, model_class, action):
    """Grant a user permission to perform an action on all instances of a model."""
    content_type = ContentType.objects.get_for_model(model_class)
    ModelPermission.objects.get_or_create(
        user=user, action=action, content_type=content_type
    )


def revoke_model_permission(user, model_class, action):
    """Revoke a user's permission to perform an action on all instances of a model."""
    content_type = ContentType.objects.get_for_model(model_class)
    ModelPermission.objects.filter(
        user=user, action=action, content_type=content_type
    ).delete()


def grant_object_permission(user, obj, action):
    """Grant a user permission to perform an action on a specific object."""
    content_type = ContentType.objects.get_for_model(obj)
    ObjectPermission.objects.get_or_create(
        user=user, action=action, content_type=content_type, object_id=obj.pk
    )


def revoke_object_permission(user, obj, action):
    """Revoke a user's permission to perform an action on a specific object."""
    content_type = ContentType.objects.get_for_model(obj)
    ObjectPermission.objects.filter(
        user=user, action=action, content_type=content_type, object_id=obj.pk
    ).delete()


def grant_group_permission(group, model_class, action):
    """Grant a group permission to perform an action on a model."""
    content_type = ContentType.objects.get_for_model(model_class)
    permission = Permission.objects.get(
        content_type=content_type, codename=f"{action}_{model_class._meta.model_name}"
    )
    group.permissions.add(permission)


def revoke_group_permission(group, model_class, action):
    """Revoke a group's permission to perform an action on a model."""
    content_type = ContentType.objects.get_for_model(model_class)
    permission = Permission.objects.get(
        content_type=content_type, codename=f"{action}_{model_class._meta.model_name}"
    )
    group.permissions.remove(permission)


def get_permitted_content_types(user, action):
    """
    Get all content types that a user has permission to perform an action on.
    
    Returns content types the user has access to via:
    - Group-based model-level permissions
    - Individual model-level permissions (ModelPermission)
    - Object-level permissions (ObjectPermission)
    """
    content_types = ContentType.objects.all()

    # dump out all the content types
    for content_type in content_types:
        print(
            f"Content type: {content_type} - {content_type.app_label}.{content_type.model} - {content_type.model_class()}",
            flush=True,
        )

    permitted_content_types = []
    for content_type in content_types:
        # Skip content types that don't have a model
        if not content_type.model_class():
            continue

        # if the content type doesn't start with apps (e.g. django.contrib.sessions), skip it
        model_class = content_type.model_class()
        if not model_class.__module__.startswith("apps."):
            continue

        # Check if user has group-based model-level permission
        if user.has_perm(
            f"{content_type.app_label}.{action}_{content_type._meta.model_name}"
        ):
            permitted_content_types.append(content_type)
        # Check if user has individual model-level permission
        elif ModelPermission.objects.filter(
            user=user, action=action, content_type=content_type
        ).exists():
            permitted_content_types.append(content_type)
        # Check if user has object-level permission
        elif ObjectPermission.objects.filter(
            user=user, action=action, content_type=content_type
        ).exists():
            permitted_content_types.append(content_type)

    return permitted_content_types


def get_permitted_objects(user, action, model_class):
    """
    Get all objects of a given model that a user has permission to perform an action on.
    
    Returns objects the user has access to via:
    - Public access rules (bioregions, related challenges)
    - Visibility flags (users, communities, projects with view_members/view_public)
    - Model-level permissions (group-based)
    - Model-level permissions (individual user via ModelPermission)
    - Object-level permissions (specific instances via ObjectPermission)
    """
    from apps.bioregions.models import Bioregion
    from apps.challenges.models import Challenge
    from apps.communities.models import Community
    from apps.projects.models import Project
    from apps.locations.models import Location
    
    # Public access rules
    if model_class == Bioregion and action == "view" and user.is_authenticated:
        # All authenticated users can view all bioregions
        return list(model_class.objects.all())
    
    if model_class == Challenge and action == "view" and user.is_authenticated:
        # All authenticated users can view challenges with a related bioregion
        return list(model_class.objects.filter(related_bioregion__isnull=False))
    
    # Visibility rules for users, communities, and projects
    if model_class == User and action == "view":
        if user.is_superuser:
            # Superusers can see everyone
            return list(model_class.objects.all())
        elif user.is_authenticated:
            # Authenticated users can see themselves + view_members users + view_public users
            from django.db.models import Q
            return list(model_class.objects.filter(
                Q(id=user.id) | Q(view_members=True) | Q(view_public=True)
            ).distinct())
        else:
            # Unauthenticated users can only see view_public users
            return list(model_class.objects.filter(view_public=True))
    
    if model_class == Community and action == "view":
        if user.is_superuser:
            # Superusers can see all communities
            return list(model_class.objects.all())
        elif user.is_authenticated:
            # Authenticated users can see their own + view_members communities + view_public communities
            from django.db.models import Q
            return list(model_class.objects.filter(
                Q(created_by=user) | Q(view_members=True) | Q(view_public=True)
            ).distinct())
        else:
            # Unauthenticated users can only see view_public communities
            return list(model_class.objects.filter(view_public=True))
    
    if model_class == Project and action == "view":
        if user.is_superuser:
            # Superusers can see all projects
            return list(model_class.objects.all())
        elif user.is_authenticated:
            # Authenticated users can see their own + view_members projects + view_public projects
            from django.db.models import Q
            return list(model_class.objects.filter(
                Q(created_by=user) | Q(view_members=True) | Q(view_public=True)
            ).distinct())
        else:
            # Unauthenticated users can only see view_public projects
            return list(model_class.objects.filter(view_public=True))

    if model_class == Location and action == "view":
        if user.is_superuser:
            return list(model_class.objects.all())
        elif user.is_authenticated:
            from django.db.models import Q
            return list(model_class.objects.filter(
                Q(created_by=user) | Q(view_members=True) | Q(view_public=True)
            ).distinct())
        else:
            return list(model_class.objects.filter(view_public=True))
    
    from apps.stories.models import Story
    if model_class == Story and action == "view":
        if user.is_superuser:
            # Superusers can see all stories
            return list(model_class.objects.all())
        elif user.is_authenticated:
            # Authenticated users can see their own + view_members stories + view_public stories
            from django.db.models import Q
            return list(model_class.objects.filter(
                Q(created_by=user) | Q(view_members=True) | Q(view_public=True)
            ).distinct())
        else:
            # Unauthenticated users can only see view_public stories
            return list(model_class.objects.filter(view_public=True))
    
    permitted_objects_by_model_permission = []
    permitted_objects_by_individual_model_permission = []
    permitted_objects_by_object_permission = []

    # Get objects through group model-level permissions
    model_permission = f"{action}_{model_class._meta.model_name}"
    if user.has_perm(f"{model_class._meta.app_label}.{model_permission}"):
        permitted_objects_by_model_permission.extend(model_class.objects.all())

    # Get objects through individual model-level permissions
    content_type = ContentType.objects.get_for_model(model_class)
    if ModelPermission.objects.filter(
        user=user, action=action, content_type=content_type
    ).exists():
        permitted_objects_by_individual_model_permission.extend(model_class.objects.all())

    # Get objects through object-level permissions
    permission_ids = ObjectPermission.objects.filter(
        user=user, action=action, content_type=content_type
    ).values_list("object_id", flat=True)
    permitted_objects_by_object_permission.extend(
        model_class.objects.filter(id__in=permission_ids)
    )

    # Return the union of all three sets
    return list(
        set(permitted_objects_by_model_permission)
        | set(permitted_objects_by_individual_model_permission)
        | set(permitted_objects_by_object_permission)
    )


def get_permitted_object(user, action, model_class, object_id):
    """Get an object of a given model that a user has permission to perform an action on."""
    try:
        obj = model_class.objects.get(id=object_id)
        content_type = ContentType.objects.get_for_model(model_class)
        obj.content_type = content_type
        obj.foo = "bar"
    except model_class.DoesNotExist:
        raise Http404

    if not is_permitted(user, action, obj):
        raise PermissionDenied

    return obj


def grant_creator_permissions(user, model_class):
    """
    Grant a user permission to:
    - Add new instances of a model
    - View, change, delete, and delegate their own created instances
    
    This is useful for giving users the ability to create and manage their own content.
    Example: grant_creator_permissions(user, Project)
    """
    grant_model_permission(user, model_class, "add")
    # Note: View, change, delete, and delegate permissions for owned objects
    # are automatically granted via the ownership check in is_permitted()


def grant_full_model_access(user, model_class):
    """
    Grant a user full access to all instances of a model.
    Grants: add, view, change, delete, and delegate permissions.
    """
    for action in ["add", "view", "change", "delete", "delegate"]:
        grant_model_permission(user, model_class, action)


def revoke_all_model_permissions(user, model_class):
    """
    Revoke all model-level permissions for a user on a specific model.
    """
    content_type = ContentType.objects.get_for_model(model_class)
    ModelPermission.objects.filter(user=user, content_type=content_type).delete()


def get_user_model_permissions(user, model_class):
    """
    Get all actions a user has model-level permission for on a specific model.
    Returns a list of action strings.
    """
    content_type = ContentType.objects.get_for_model(model_class)
    return list(
        ModelPermission.objects.filter(
            user=user, content_type=content_type
        ).values_list("action", flat=True)
    )
