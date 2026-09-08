from django.db.models import Q
from .models import Commons


def get_visible_commons_queryset(user):
    """Commons a user is permitted to view, for use in querysets/pickers."""
    if not user or not user.is_authenticated:
        return Commons.objects.filter(view_public=True)
    if user.is_superuser:
        return Commons.objects.all()
    return Commons.objects.filter(
        Q(created_by=user) | Q(owners=user) | Q(admins=user) | Q(members=user)
        | Q(view_members=True) | Q(view_public=True)
    )


def get_user_commons_queryset(user):
    """Commons a user belongs to (owner/admin/member) - used to populate visible_to_commons pickers."""
    if not user or not user.is_authenticated:
        return Commons.objects.none()
    if user.is_superuser:
        return Commons.objects.all()
    return Commons.objects.filter(
        Q(owners=user) | Q(admins=user) | Q(members=user)
    )
