from django.db.models import Q
from .models import Bioregion


def get_visible_bioregion_queryset(user):
    """Bioregions a user is permitted to view, for use in ModelChoiceField/PrimaryKeyRelatedField querysets."""
    if not user or not user.is_authenticated:
        return Bioregion.objects.filter(view_public=True)
    if user.is_superuser:
        return Bioregion.objects.all()
    return Bioregion.objects.filter(
        Q(created_by=user) | Q(owners=user) | Q(admins=user) | Q(members=user)
        | Q(users=user) | Q(view_members=True) | Q(view_public=True)
    ).distinct()
