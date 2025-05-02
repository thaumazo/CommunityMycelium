from django import template
from django.contrib.contenttypes.models import ContentType
from ..utils import can

register = template.Library()

@register.filter
def content_type_id(obj):
    """Get the content type ID for a model instance."""
    return ContentType.objects.get_for_model(obj).id

@register.filter
def can(user, permission_str):
    """Check if a user has permission to perform an action on an object.
    
    Usage: {{ user|can:"action:object" }}
    Example: {{ user|can:"delegate:meeting" }}
    """
    try:
        action, obj_id = permission_str.split(':', 1)
        # Get the meeting object
        from apps.meetings.models import Meeting
        meeting = Meeting.objects.get(id=obj_id)
        # Check if the user has the permission
        return can(user, action, meeting)
    except (ValueError, AttributeError, Meeting.DoesNotExist):
        return False 