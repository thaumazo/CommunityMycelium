from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from .models import Community
from apps.acl.utils import grant_object_permission, revoke_object_permission
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from PIL import Image
from django.core.files.base import ContentFile
import os


@receiver(post_save, sender=Community)
def grant_community_creator_permissions(sender, instance, created, **kwargs):
    """Grant all permissions to the community creator when the community is created."""
    if created and instance.created_by:
        # Get all permissions for Community model
        community_permissions = Permission.objects.filter(
            content_type=ContentType.objects.get_for_model(Community)
        )
        for permission in community_permissions:
            # Extract the base action from the permission codename (e.g., "add_community" -> "add")
            base_action = permission.codename.split("_")[0]
            grant_object_permission(instance.created_by, instance, base_action)


@receiver(pre_delete, sender=Community)
def delete_community_permissions(sender, instance, **kwargs):
    """Delete all permissions for a community when it is deleted."""
    # Get all permissions for this community and delete them
    for permission in instance.permissions.all():
        revoke_object_permission(permission.user, instance, permission.action)


@receiver(pre_save, sender=Community)
def generate_community_thumbnail(sender, instance, **kwargs):
    """Generate a thumbnail when a community picture is uploaded."""
    if instance.picture:
        try:
            # Open the uploaded image
            img = Image.open(instance.picture)
            
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create a white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Create thumbnail
            img.thumbnail((200, 200), Image.Resampling.LANCZOS)
            
            # Save to a ContentFile
            thumb_io = ContentFile(b'')
            img.save(thumb_io, format='JPEG', quality=85)
            
            # Generate thumbnail filename
            original_name = os.path.basename(instance.picture.name)
            name_without_ext = os.path.splitext(original_name)[0]
            thumb_name = f"{name_without_ext}_thumb.jpg"
            
            # Save the thumbnail
            instance.picture_thumbnail.save(thumb_name, thumb_io, save=False)
        except Exception as e:
            # If thumbnail generation fails, just continue without a thumbnail
            print(f"Error generating thumbnail: {e}")
