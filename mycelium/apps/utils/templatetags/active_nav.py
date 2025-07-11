from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def active_class(context, url_names_or_prefix, css_class="active"):
    """
    Usage:
    1) {% active_class 'home' %}
    2) {% active_class 'meeting_list,meeting_detail' %}
    3) {% active_class 'meeting_*' %}
    """
    try:
        current_url_name = context["request"].resolver_match.url_name
        if url_names_or_prefix.endswith("*"):
            prefix = url_names_or_prefix[:-1]
            if current_url_name.startswith(prefix):
                return css_class
        else:
            url_names = [name.strip() for name in url_names_or_prefix.split(",")]
            if current_url_name in url_names:
                return css_class
    except (AttributeError, KeyError):
        pass
    return ""
