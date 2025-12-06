from django.core.management.base import BaseCommand
from apps.stories.models import StoryMedia


class Command(BaseCommand):
    help = 'Convert existing YouTube URLs to embed format'

    def handle(self, *args, **options):
        video_urls = StoryMedia.objects.filter(media_type='video_url', url__isnull=False)
        count = 0
        
        for media in video_urls:
            old_url = media.url
            # The save method will automatically convert the URL
            media.save()
            
            if old_url != media.url:
                count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Converted: {old_url} → {media.url}')
                )
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No URLs needed conversion.'))
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully converted {count} video URL(s).')
            )
