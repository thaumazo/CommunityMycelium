from django.contrib import admin
from .models import Commons, CommonsApplication, CommonsInvite


@admin.register(Commons)
class CommonsAdmin(admin.ModelAdmin):
    list_display = ("title", "bioregion", "created_by", "view_members", "view_public")
    search_fields = ("title", "description")


@admin.register(CommonsApplication)
class CommonsApplicationAdmin(admin.ModelAdmin):
    list_display = ("commons", "applicant", "status", "created_at")
    list_filter = ("status",)


@admin.register(CommonsInvite)
class CommonsInviteAdmin(admin.ModelAdmin):
    list_display = ("commons", "invited_user", "invited_by", "status", "created_at")
    list_filter = ("status",)
