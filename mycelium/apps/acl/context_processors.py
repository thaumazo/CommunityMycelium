def view_simulation_context(request):
    """Expose the current user's visibility-preview state and choices to all templates."""
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {}

    from apps.commons.utils import get_user_commons_queryset

    return {
        "view_simulation": getattr(request, "view_simulation", None),
        "view_simulation_commons_choices": get_user_commons_queryset(user).order_by("title"),
    }
