from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = "user"


class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "get_role",
    )
    list_select_related = ("profile",)

    def get_role(self, instance):
        roles = []
        if instance.profile.is_viewer:
            roles.append("Viewer")
        if instance.profile.is_editor:
            roles.append("Editor")
        if instance.profile.is_admin:
            roles.append("Admin")
        return ", ".join(roles) if roles else "No Role"

    get_role.short_description = "Role"

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)


class GroupAdmin(admin.ModelAdmin):
    list_display = ("name", "get_permissions")
    filter_horizontal = ("permissions",)

    def get_permissions(self, obj):
        return ", ".join([p.name for p in obj.permissions.all()])


admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
admin.site.register(User, CustomUserAdmin)
