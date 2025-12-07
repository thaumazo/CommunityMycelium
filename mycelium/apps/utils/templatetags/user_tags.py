from django import template
from apps.acl.utils import is_permitted
from django.contrib.auth import get_user_model

User = get_user_model()
register = template.Library()


@register.simple_tag
def can(user, action, obj):
    """Check if a user can perform an action on an object.
    Usage: {% can request.user 'change' meeting %}
    """
    return is_permitted(user, action, obj)


@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary by key.
    Usage: {{ story_attachments|get_item:key }}
    """
    if not dictionary:
        return None
    
    return dictionary.get(key)


@register.simple_tag
def get_stories_for(story_attachments, element_type, element_id):
    """Get stories for a specific element.
    Usage: {% get_stories_for story_attachments 'socialrole' socialrole.id as stories %}
    """
    if not story_attachments:
        return []
    
    key = f'{element_type}_{element_id}'
    return story_attachments.get(key, [])


@register.filter
def youtube_embed(url):
    """Convert YouTube URL to embed format.
    Handles:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID (already embed format)
    """
    import re
    
    if not url:
        return url
    
    # Already in embed format
    if '/embed/' in url:
        return url
    
    # Extract video ID from watch?v= format
    watch_match = re.search(r'[?&]v=([^&]+)', url)
    if watch_match:
        video_id = watch_match.group(1)
        return f'https://www.youtube.com/embed/{video_id}'
    
    # Extract video ID from youtu.be format
    short_match = re.search(r'youtu\.be/([^?&]+)', url)
    if short_match:
        video_id = short_match.group(1)
        return f'https://www.youtube.com/embed/{video_id}'
    
    # Return original URL if no match (might be Vimeo or other)
    return url


@register.filter
def get_pending_users_count(user):
    """Get count of users pending approval (for superuser badge).
    Usage: {{ request.user|get_pending_users_count }}
    """
    if not user.is_superuser:
        return 0
    
    return User.objects.filter(is_approved=False, is_active=False).count()


@register.filter
def get_pending_users_count(user):
    """Get count of pending user registrations (superuser only).
    Usage: {{ request.user|get_pending_users_count }}
    """
    if not user.is_authenticated or not user.is_superuser:
        return 0
    
    return User.objects.filter(is_approved=False, is_active=False).count()
