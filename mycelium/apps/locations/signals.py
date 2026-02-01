from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from .models import Location
from apps.acl.utils import grant_object_permission, revoke_object_permission
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from PIL import Image
from django.core.files.base import ContentFile
import os


@receiver(post_save, sender=Location)
def grant_location_creator_permissions(sender, instance, created, **kwargs):
    """Grant all permissions to the location creator when the location is created."""
    if created and instance.created_by:
        location_permissions = Permission.objects.filter(
            content_type=ContentType.objects.get_for_model(Location)
        )
        for permission in location_permissions:
            base_action = permission.codename.split("_")[0]
            grant_object_permission(instance.created_by, instance, base_action)


@receiver(pre_delete, sender=Location)
def delete_location_permissions(sender, instance, **kwargs):
    """Delete all permissions for a location when it is deleted."""
    for permission in instance.permissions.all():
        revoke_object_permission(permission.user, instance, permission.action)


@receiver(pre_save, sender=Location)
def generate_location_thumbnail(sender, instance, **kwargs):
    """Generate a thumbnail when a location picture is uploaded."""
    if instance.picture:
        try:
            img = Image.open(instance.picture)

            if img.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
                img = background
            elif img.mode != "RGB":
                img = img.convert("RGB")

            img.thumbnail((200, 200), Image.Resampling.LANCZOS)

            thumb_io = ContentFile(b"")
            img.save(thumb_io, format="JPEG", quality=85)

            original_name = os.path.basename(instance.picture.name)
            name_without_ext = os.path.splitext(original_name)[0]
            thumb_name = f"{name_without_ext}_thumb.jpg"

            instance.picture_thumbnail.save(thumb_name, thumb_io, save=False)
        except Exception as e:
            print(f"Error generating thumbnail: {e}")
