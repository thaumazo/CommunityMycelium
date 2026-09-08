from django.db.models import Q
from django.contrib.auth import get_user_model

User = get_user_model()


def get_visible_user_queryset(user):
    """Users a given user is permitted to see, for use in ModelChoiceField/ModelMultipleChoiceField querysets."""
    if not user or not user.is_authenticated:
        return User.objects.filter(view_public=True)
    if user.is_superuser:
        return User.objects.all()
    return User.objects.filter(
        Q(id=user.id) | Q(view_members=True) | Q(view_public=True)
        | Q(visible_to_commons__owners=user) | Q(visible_to_commons__admins=user) | Q(visible_to_commons__members=user)
    )
