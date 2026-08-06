from django import template
from functools import lru_cache
from posixpath import basename, dirname
import re

from django.contrib.staticfiles import finders
from django.utils.text import slugify

register = template.Library()


DECK_IMAGE_PREFIXES = (
    "img/roles/",
    "img/capitals/",
    "img/maladaptives/",
    "img/metacrisis_facets/",
)


@lru_cache(maxsize=4096)
def _static_asset_exists(relative_path):
    return bool(finders.find(relative_path))


def _normalize_relative_static_path(path):
    if not path:
        return ""
    return str(path).replace("\\", "/").lstrip("/")


def _strip_thumbnail_suffix(filename):
    match = re.match(r"^(.*)_\d+(\.[^./]+)$", filename)
    if not match:
        return filename
    return f"{match.group(1)}{match.group(2)}"


@register.filter(name='thumbnail')
def thumbnail(image_path, size=80):
    """
    Add _<size> suffix before file extension to get thumbnail version.
    
    Usage:
        {{ image_path|thumbnail }}          # Returns path_80.ext
        {{ image_path|thumbnail:120 }}      # Returns path_120.ext
    
    Examples:
        'img/example.png' -> 'img/example_80.png'
        'img/example.png'|thumbnail:120 -> 'img/example_120.png'
    """
    if not image_path:
        return image_path
    
    if '.' in image_path:
        parts = image_path.rsplit('.', 1)
        return f"{parts[0]}_{size}.{parts[1]}"
    
    return image_path


@register.filter(name='alternate_deck')
def alternate_deck(image_path, user=None):
    normalized_path = _normalize_relative_static_path(image_path)
    if not normalized_path:
        return image_path

    deck_slug = slugify(getattr(user, "alternate_deck", "") or "")
    if not deck_slug:
        return image_path

    if not any(normalized_path.startswith(prefix) for prefix in DECK_IMAGE_PREFIXES):
        return image_path

    folder = dirname(normalized_path)
    filename = basename(normalized_path)
    candidate = f"{folder}/{deck_slug}/{filename}" if folder else f"{deck_slug}/{filename}"

    if _static_asset_exists(candidate):
        return candidate

    # If an explicit thumbnail override does not exist (e.g. *_80.png),
    # allow fallback to a full-size alternate image in the same deck folder.
    unsuffixed_filename = _strip_thumbnail_suffix(filename)
    if unsuffixed_filename != filename:
        fallback_candidate = f"{folder}/{deck_slug}/{unsuffixed_filename}" if folder else f"{deck_slug}/{unsuffixed_filename}"
        if _static_asset_exists(fallback_candidate):
            return fallback_candidate

    return image_path
