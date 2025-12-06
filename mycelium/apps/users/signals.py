from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.files.base import ContentFile
from PIL import Image
import io
import os
from .models import User


@receiver(pre_save, sender=User)
def generate_thumbnail(sender, instance, **kwargs):
    """
    Generate a thumbnail when a user uploads a picture.
    Thumbnail is 200x200px, optimized for web use.
    """
    if not instance.picture:
        # If no picture, clear the thumbnail
        instance.picture_thumbnail = None
        return
    
    # Check if picture has changed
    try:
        old_instance = User.objects.get(pk=instance.pk)
        if old_instance.picture == instance.picture:
            # Picture hasn't changed, don't regenerate thumbnail
            return
    except User.DoesNotExist:
        # New user, generate thumbnail
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


@receiver(post_save, sender=User)
def cleanup_old_images(sender, instance, **kwargs):
    """
    Clean up old image files when they're replaced.
    This runs after save to avoid deleting the new file.
    """
    # This is a placeholder for future cleanup logic if needed
    pass
