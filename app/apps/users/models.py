from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    pass


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    is_viewer = models.BooleanField(default=True)
    is_editor = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def clean(self):
        """Enforce role hierarchy"""
        if self.is_admin:
            self.is_editor = True
            self.is_viewer = True
        elif self.is_editor:
            self.is_viewer = True

    def save(self, *args, **kwargs):
        # Ensure role hierarchy
        self.clean()

        # Get or create groups
        viewer_group, _ = Group.objects.get_or_create(name="viewer")
        editor_group, _ = Group.objects.get_or_create(name="editor")
        admin_group, _ = Group.objects.get_or_create(name="admin")

        # Update group membership based on role flags
        if self.is_viewer:
            self.user.groups.add(viewer_group)
        else:
            self.user.groups.remove(viewer_group)

        if self.is_editor:
            self.user.groups.add(editor_group)
        else:
            self.user.groups.remove(editor_group)

        if self.is_admin:
            self.user.groups.add(admin_group)
        else:
            self.user.groups.remove(admin_group)

        super().save(*args, **kwargs)
