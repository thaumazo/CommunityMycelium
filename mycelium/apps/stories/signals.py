from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import StoryMedia
from PIL import Image
from django.core.files.base import ContentFile
import os


@receiver(pre_save, sender=StoryMedia)
def generate_media_thumbnail(sender, instance, **kwargs):
    """Generate a thumbnail for image media."""
    if instance.file and instance.media_type == 'image':
        try:
            # Open the uploaded image
            img = Image.open(instance.file)
            
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
            img.thumbnail((400, 400), Image.Resampling.LANCZOS)
            
            # Save to a ContentFile
            thumb_io = ContentFile(b'')
            img.save(thumb_io, format='JPEG', quality=85)
            
            # Generate thumbnail filename
            original_name = os.path.basename(instance.file.name)
            name_without_ext = os.path.splitext(original_name)[0]
            thumb_name = f"{name_without_ext}_thumb.jpg"
            
            # Save the thumbnail
            instance.file_thumbnail.save(thumb_name, thumb_io, save=False)
        except Exception as e:
            # If thumbnail generation fails, just continue without a thumbnail
            print(f"Error generating thumbnail: {e}")
