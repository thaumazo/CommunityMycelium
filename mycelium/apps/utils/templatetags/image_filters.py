from django import template

register = template.Library()


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
