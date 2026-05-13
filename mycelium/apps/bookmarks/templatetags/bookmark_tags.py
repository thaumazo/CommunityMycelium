from django import template
from django.contrib.contenttypes.models import ContentType

from apps.bookmarks.models import Bookmark

register = template.Library()


@register.simple_tag
def object_content_type(obj):
    if not obj:
        return None
    return ContentType.objects.get_for_model(obj, for_concrete_model=False)


@register.simple_tag
def object_detail_url(obj):
    if not obj:
        return None

    content_type = ContentType.objects.get_for_model(obj, for_concrete_model=False)
    url_name = f'{content_type.model}_detail'

    from django.urls import NoReverseMatch, reverse

    try:
        return reverse(url_name, args=[obj.pk])
    except NoReverseMatch:
        return None


@register.simple_tag
def bookmark_state(user, obj):
    if not user or not user.is_authenticated or not obj:
        return False

    content_type = ContentType.objects.get_for_model(obj, for_concrete_model=False)
    return Bookmark.objects.filter(
        user=user,
        content_type=content_type,
        object_id=obj.pk,
    ).exists()
