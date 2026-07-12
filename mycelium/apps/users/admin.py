from django.contrib import admin
from .models import User, UserInvite


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'full_name', 'invite_role', 'is_staff', 'is_active']
    list_filter = ['invite_role', 'is_staff', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'full_name']
    ordering = ['username']


@admin.register(UserInvite)
class UserInviteAdmin(admin.ModelAdmin):
    list_display = ["token", "inviter", "invited_email", "invited_user", "status", "approved_by", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["token", "inviter__username", "invited_email", "invited_user__username"]
