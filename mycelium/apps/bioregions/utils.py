from django.db.models import Q
from .models import Bioregion


def get_visible_bioregion_queryset(user):
    """Bioregions a user is permitted to view, for use in ModelChoiceField/PrimaryKeyRelatedField querysets."""
    if not user or not user.is_authenticated:
        return Bioregion.objects.filter(view_public=True)
    if user.is_superuser:
        return Bioregion.objects.all()
    # Callers combine this with other querysets via `|`, which requires matching
    # `distinct` flags; leave undistinct here and let callers dedupe afterwards.
    return Bioregion.objects.filter(
        Q(created_by=user) | Q(owners=user) | Q(admins=user) | Q(members=user)
        | Q(users=user) | Q(view_members=True) | Q(view_public=True)
        | Q(visible_to_commons__owners=user) | Q(visible_to_commons__admins=user) | Q(visible_to_commons__members=user)
    )
