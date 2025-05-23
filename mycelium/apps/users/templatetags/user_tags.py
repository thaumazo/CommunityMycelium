from django import template
from apps.acl.utils import is_permitted

register = template.Library()


@register.simple_tag
def can(user, action, obj):
    """Check if a user can perform an action on an object.
    Usage: {% can request.user 'change' meeting %}
    """
    return is_permitted(user, action, obj)
