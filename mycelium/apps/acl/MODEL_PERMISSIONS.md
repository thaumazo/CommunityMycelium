# ACL Model-Level Permissions

## Overview

The ACL system now supports both **model-level** and **object-level** permissions for individual users.

### Permission Hierarchy

When checking if a user has permission, the system checks in this order:

1. **Self-permission**: User accessing their own User object
2. **Ownership**: User created the object (via `created_by` field)
3. **Group model-level**: Permissions assigned to groups
4. **Individual model-level**: `ModelPermission` - permissions on all instances of a model type
5. **Object-level**: `ObjectPermission` - permissions on specific object instances

## Models

### ModelPermission
Grants a user permission to perform an action on **all instances** of a model type.

**Fields:**
- `user`: The user being granted permission
- `action`: The action (add, view, change, delete, delegate)
- `content_type`: The model type (e.g., Project, Community)

### ObjectPermission
Grants a user permission to perform an action on a **specific object instance**.

**Fields:**
- `user`: The user being granted permission
- `action`: The action (add, view, change, delete, delegate)
- `content_type`: The model type
- `object_id`: The specific object ID
- `content_object`: Generic foreign key to the object

## Common Use Cases

### Use Case 1: Creator Permissions
Give a user the ability to create projects and manage only their own:

```python
from apps.acl.utils import grant_creator_permissions
from apps.projects.models import Project

# Grant user ability to add projects
# They automatically get view/change/delete/delegate on their own created projects
grant_creator_permissions(user, Project)
```

**Result:** User can:
- ✅ Add new projects
- ✅ View their own projects (via ownership)
- ✅ Change their own projects (via ownership)
- ✅ Delete their own projects (via ownership)
- ✅ Delegate permissions on their own projects (via ownership)
- ❌ View/modify projects created by others (unless granted separately)

### Use Case 2: Full Model Access
Give a user full access to all instances of a model:

```python
from apps.acl.utils import grant_full_model_access
from apps.communities.models import Community

# Grant user full access to all communities
grant_full_model_access(user, Community)
```

**Result:** User can perform all actions on all communities.

### Use Case 3: Specific Model Permissions
Grant specific permissions manually:

```python
from apps.acl.utils import grant_model_permission, revoke_model_permission
from apps.meetings.models import Meeting

# Grant view permission on all meetings
grant_model_permission(user, Meeting, "view")

# Grant change permission on all meetings
grant_model_permission(user, Meeting, "change")

# Revoke change permission
revoke_model_permission(user, Meeting, "change")
```

### Use Case 4: Mixed Permissions
Combine model-level and object-level permissions:

```python
from apps.acl.utils import grant_model_permission, grant_object_permission
from apps.projects.models import Project

# User can add projects
grant_model_permission(user, Project, "add")

# User can view all projects
grant_model_permission(user, Project, "view")

# User can change only specific projects
specific_project = Project.objects.get(id=123)
grant_object_permission(user, specific_project, "change")
grant_object_permission(user, specific_project, "delete")
```

## Utility Functions

### Granting Permissions

```python
# Grant model-level permission
grant_model_permission(user, ModelClass, action)

# Grant object-level permission
grant_object_permission(user, object_instance, action)

# Grant creator permissions (add + ownership)
grant_creator_permissions(user, ModelClass)

# Grant full model access
grant_full_model_access(user, ModelClass)
```

### Revoking Permissions

```python
# Revoke model-level permission
revoke_model_permission(user, ModelClass, action)

# Revoke object-level permission
revoke_object_permission(user, object_instance, action)

# Revoke all model permissions
revoke_all_model_permissions(user, ModelClass)
```

### Checking Permissions

```python
# Check if user has permission
if is_permitted(user, "view", object_instance):
    # User can view this object
    pass

# Check on model (not instance)
if is_permitted(user, "add", "projects.project"):
    # User can add projects
    pass

# Get all permitted objects
permitted_projects = get_permitted_objects(user, "view", Project)

# Get specific permitted object (raises PermissionDenied if not allowed)
project = get_permitted_object(user, "change", Project, project_id)

# Get user's model permissions
actions = get_user_model_permissions(user, Project)
# Returns: ['add', 'view']
```

## Available Actions

- `add`: Create new instances
- `view`: Read/view instances
- `change`: Modify instances
- `delete`: Delete instances
- `delegate`: Grant/revoke permissions to others

## Example: Setting Up a New User

```python
from apps.users.models import User
from apps.projects.models import Project
from apps.communities.models import Community
from apps.acl.utils import grant_creator_permissions, grant_model_permission

# Get or create user
user = User.objects.get(username='john')

# Let them create and manage their own projects
grant_creator_permissions(user, Project)

# Let them view all communities
grant_model_permission(user, Community, "view")

# Let them create new communities
grant_model_permission(user, Community, "add")
```

Now John can:
- Create projects and fully manage his own projects
- View all communities in the system
- Create new communities (and then manage his own via ownership)

## Migration

After implementing these changes, run:

```bash
python manage.py makemigrations acl
python manage.py migrate acl
```

## Admin Interface

Both `ModelPermission` and `ObjectPermission` are registered in the Django admin and can be managed at:
- `/admin/acl/modelpermission/`
- `/admin/acl/objectpermission/`

## Notes

- **Ownership trumps everything**: If a user created an object (has `created_by` field), they automatically have all permissions on it
- **Model permissions are broader**: Granting a model-level permission gives access to ALL instances
- **Object permissions are specific**: Use when you need fine-grained control
- **Groups still work**: The existing Django group-based permissions continue to work alongside these individual permissions
