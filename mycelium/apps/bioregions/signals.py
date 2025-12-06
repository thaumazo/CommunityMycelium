from django.db.models.signals import post_save, pre_save, pre_delete
from django.dispatch import receiver
from django.core.files.base import ContentFile
from PIL import Image
import io
import os
from .models import Bioregion
from apps.acl.utils import grant_object_permission, revoke_object_permission
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


@receiver(post_save, sender=Bioregion)
def grant_bioregion_creator_permissions(sender, instance, created, **kwargs):
    """Grant all permissions to the bioregion creator when the bioregion is created."""
    if created and instance.created_by:
        # Get all permissions for Bioregion model
        bioregion_permissions = Permission.objects.filter(
            content_type=ContentType.objects.get_for_model(Bioregion)
        )
        for permission in bioregion_permissions:
            # Extract the base action from the permission codename (e.g., "add_bioregion" -> "add")
            base_action = permission.codename.split("_")[0]
            grant_object_permission(instance.created_by, instance, base_action)


@receiver(pre_save, sender=Bioregion)
def generate_bioregion_thumbnail(sender, instance, **kwargs):
    """
    Generate a thumbnail when a bioregion picture is uploaded.
    Thumbnail is 200x200px, optimized for web use.
    """
    if not instance.picture:
        # If no picture, clear the thumbnail
        instance.picture_thumbnail = None
        return
    
    # Check if picture has changed
    try:
        old_instance = Bioregion.objects.get(pk=instance.pk)
        if old_instance.picture == instance.picture:
            # Picture hasn't changed, don't regenerate thumbnail
            return
    except Bioregion.DoesNotExist:
        # New bioregion, generate thumbnail
        pass
    
    # Open the uploaded image
    img = Image.open(instance.picture)
    
    # Convert to RGB if necessary (handles PNG with transparency)
    if img.mode in ('RGBA', 'LA', 'P'):
        # Create a white background
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Create thumbnail (200x200, preserving aspect ratio)
    img.thumbnail((200, 200), Image.Resampling.LANCZOS)
    
    # Save to BytesIO
    thumb_io = io.BytesIO()
    img.save(thumb_io, format='JPEG', quality=85, optimize=True)
    thumb_io.seek(0)
    
    # Generate filename
    original_name = os.path.basename(instance.picture.name)
    name_without_ext = os.path.splitext(original_name)[0]
    thumbnail_name = f"{name_without_ext}_thumb.jpg"
    
    # Save the thumbnail
    instance.picture_thumbnail.save(
        thumbnail_name,
        ContentFile(thumb_io.read()),
        save=False
    )


@receiver(pre_delete, sender=Bioregion)
def delete_bioregion_permissions(sender, instance, **kwargs):
    """Delete all permissions for a bioregion when it is deleted."""
    # Get all permissions for this bioregion and delete them
    for permission in instance.permissions.all():
        revoke_object_permission(permission.user, instance, permission.action)
