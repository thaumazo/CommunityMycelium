from django.contrib import admin
from apps.bioregions.models import Bioregion
from .models import BioregionRequest, User, UserInvite


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'full_name', 'onboarding_status', 'invite_role', 'is_staff', 'is_active']
    list_filter = ['onboarding_status', 'invite_role', 'is_staff', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'full_name']
    ordering = ['username']


@admin.register(UserInvite)
class UserInviteAdmin(admin.ModelAdmin):
    list_display = ["token", "inviter", "invited_email", "invited_user", "status", "approved_by", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["token", "inviter__username", "invited_email", "invited_user__username"]


@admin.register(BioregionRequest)
class BioregionRequestAdmin(admin.ModelAdmin):
    list_display = ["title", "requested_by", "status", "reviewed_by", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["title", "requested_by__username"]

    def save_model(self, request, obj, form, change):
        if obj.status == BioregionRequest.STATUS_APPROVED and obj.created_bioregion_id is None:
            bioregion = Bioregion.objects.create(
                title=obj.title,
                description=obj.description,
                created_by=request.user,
            )
            obj.created_bioregion = bioregion
            obj.reviewed_by = request.user
            from django.utils import timezone
            obj.reviewed_at = timezone.now()
            bioregion.members.add(obj.requested_by)
        elif obj.status == BioregionRequest.STATUS_DECLINED and obj.reviewed_by_id is None:
            obj.reviewed_by = request.user
            from django.utils import timezone
            obj.reviewed_at = timezone.now()
        super().save_model(request, obj, form, change)
