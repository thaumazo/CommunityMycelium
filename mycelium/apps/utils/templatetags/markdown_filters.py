from django import template
from django.utils.safestring import mark_safe
import markdown
import bleach

register = template.Library()

# Define allowed HTML tags for safe rendering
ALLOWED_TAGS = [
    'p', 'br', 'span', 'em', 'strong', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'a', 'img',
    'table', 'thead', 'tbody', 'tr', 'th', 'td'
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target'],
    'img': ['src', 'alt', 'title'],
    'code': ['class'],
    'pre': ['class'],
}


@register.filter(is_safe=True)
def markdown_to_html(text):
    """
    Convert markdown text to safe HTML.
    Usage: {{ description|markdown_to_html }}
    """
    if not text:
        return ''
    
    # Convert markdown to HTML
    html = markdown.markdown(
        text,
        extensions=['nl2br', 'tables', 'fenced_code'],
        extension_configs={
            'markdown.extensions.codehilite': {
                'use_pygments': False,
            }
        }
    )
    
    # Sanitize HTML to prevent XSS
    safe_html = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=False
    )
    
    return mark_safe(safe_html)


@register.filter(is_safe=True)
def markdown_to_html_escaped(text):
    """
    Convert markdown text to safe HTML with escaped dangerous content.
    Usage: {{ description|markdown_to_html_escaped }}
    """
    if not text:
        return ''
    
    # Convert markdown to HTML
    html = markdown.markdown(
        text,
        extensions=['nl2br', 'tables', 'fenced_code'],
        extension_configs={
            'markdown.extensions.codehilite': {
                'use_pygments': False,
            }
        }
    )
    
    # Sanitize HTML to prevent XSS - strip dangerous tags
    safe_html = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )
    
    return mark_safe(safe_html)
