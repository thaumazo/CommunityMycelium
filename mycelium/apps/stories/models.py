from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from apps.acl.models import ObjectPermission

User = get_user_model()


class Story(models.Model):
    """
    Core story model for warm data narratives.
    Stories can be attached to multiple objects (projects, facets, etc.)
    """
    NOTE_TYPE_NONE = "none"
    NOTE_TYPE_IDEA = "idea"
    NOTE_TYPE_OFFER = "offer"

    NOTE_TYPE_CHOICES = [
        (NOTE_TYPE_NONE, "None"),
        (NOTE_TYPE_IDEA, "Idea"),
        (NOTE_TYPE_OFFER, "Offer"),
    ]

    COMMUNITY_NOTE_PENDING = "pending"
    COMMUNITY_NOTE_PROMOTED = "promoted"
    COMMUNITY_NOTE_DECLINED = "declined"

    COMMUNITY_NOTE_STATUS_CHOICES = [
        (COMMUNITY_NOTE_PENDING, "Pending"),
        (COMMUNITY_NOTE_PROMOTED, "Promoted"),
        (COMMUNITY_NOTE_DECLINED, "Declined"),
    ]

    title = models.CharField(max_length=255)
    text_content = models.TextField(
        blank=True,
        help_text="The main narrative content of the story"
    )
    youtube_url = models.URLField(
        blank=True,
        null=True,
        help_text="YouTube video URL to embed (e.g., https://www.youtube.com/watch?v=...)"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="authored_stories"
    )
    
    view_members = models.BooleanField(
        default=False,
        help_text="Authenticated members can view this story.",
    )
    
    view_public = models.BooleanField(
        default=False,
        help_text="Public (unauthenticated) users can view this story.",
    )

    is_community_note = models.BooleanField(
        default=False,
        help_text="Whether this story was submitted as a project community note.",
    )

    community_note_type = models.CharField(
        max_length=20,
        choices=NOTE_TYPE_CHOICES,
        default=NOTE_TYPE_NONE,
        help_text="Type of community note (idea or offer).",
    )

    community_note_status = models.CharField(
        max_length=20,
        choices=COMMUNITY_NOTE_STATUS_CHOICES,
        default=COMMUNITY_NOTE_PENDING,
        help_text="Decision status for community note review.",
    )

    community_note_decided_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="decided_community_notes",
        blank=True,
        null=True,
    )

    community_note_decided_at = models.DateTimeField(
        blank=True,
        null=True,
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    permissions = GenericRelation(ObjectPermission)
    
    class Meta:
        verbose_name_plural = "stories"
        ordering = ['-created_at']
        permissions = [
            ("delegate_story", "Can delegate story"),
        ]
    
    def __str__(self):
        return f"{self.title} by {self.created_by.username}"

    def get_youtube_embed_url(self):
        """Return a robust YouTube embed URL for the story's youtube_url.
        Supports watch URLs (v=ID), youtu.be short URLs, and existing embed URLs.
        Preserves query parameters like si= for proper embedding.
        """
        url = getattr(self, "youtube_url", None)
        if not url:
            return None

        import re
        from urllib.parse import urlparse, parse_qs, urlencode
        
        u = url.strip()

        # Already in embed format - return as is
        if "/embed/" in u:
            return u

        # Parse URL to extract video ID and preserve parameters
        parsed = urlparse(u)
        query_params = parse_qs(parsed.query)
        
        video_id = None
        
        # Standard watch URL (youtube.com/watch?v=ID)
        if 'v' in query_params:
            video_id = query_params['v'][0]
            # Remove 'v' from params since it's now in the path
            del query_params['v']
        # Short youtu.be URL
        elif 'youtu.be' in parsed.netloc:
            video_id = parsed.path.lstrip('/')
        
        if video_id:
            # Build embed URL preserving other params like si=
            embed_url = f"https://www.youtube.com/embed/{video_id}"
            if query_params:
                # Flatten query params back to string
                params_str = urlencode({k: v[0] for k, v in query_params.items()})
                embed_url += f"?{params_str}"
            return embed_url
        
        # For other platforms or unrecognized formats, return original URL
        return u


class StoryMedia(models.Model):
    """
    Media assets (images, videos) attached to stories.
    Supports multiple media items per story with ordering.
    """
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video_url', 'Video URL'),
    ]
    
    story = models.ForeignKey(
        Story,
        on_delete=models.CASCADE,
        related_name="media"
    )
    media_type = models.CharField(
        max_length=20,
        choices=MEDIA_TYPE_CHOICES
    )
    file = models.ImageField(
        upload_to='story_media/',
        blank=True,
        null=True,
        help_text="Image file"
    )
    file_thumbnail = models.ImageField(
        upload_to='story_media/thumbnails/',
        blank=True,
        null=True,
        editable=False,
        help_text="Automatically generated thumbnail for images"
    )
    url = models.URLField(
        blank=True,
        null=True,
        help_text="URL for embedded videos (YouTube, Vimeo, etc.)"
    )
    caption = models.TextField(
        blank=True,
        help_text="Caption or description for this media"
    )
    order = models.IntegerField(
        default=0,
        help_text="Display order (lower numbers appear first)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name_plural = "story media"
    
    def save(self, *args, **kwargs):
        """Convert YouTube URLs to embed format before saving."""
        if self.media_type == 'video_url' and self.url:
            self.url = self._convert_to_embed_url(self.url)
        super().save(*args, **kwargs)
    
    def _convert_to_embed_url(self, url):
        """Convert YouTube URL to embed format, preserving parameters."""
        import re
        from urllib.parse import urlparse, parse_qs, urlencode
        
        if not url:
            return url
        
        u = url.strip()
        
        # Already in embed format - return as is
        if '/embed/' in u:
            return u
        
        # Parse URL
        parsed = urlparse(u)
        query_params = parse_qs(parsed.query)
        
        video_id = None
        
        # Extract video ID from watch?v= format
        if 'v' in query_params:
            video_id = query_params['v'][0]
            del query_params['v']
        # Extract video ID from youtu.be format
        elif 'youtu.be' in parsed.netloc:
            video_id = parsed.path.lstrip('/')
        
        if video_id:
            embed_url = f'https://www.youtube.com/embed/{video_id}'
            if query_params:
                params_str = urlencode({k: v[0] for k, v in query_params.items()})
                embed_url += f'?{params_str}'
            return embed_url
        
        # Return original URL if no match (might be Vimeo or other)
        return url

    def get_embed_url(self):
        """Return an embed-safe URL based on stored url.
        Handles existing non-embedded YouTube URLs and leaves other platforms unchanged.
        """
        if not self.url:
            return None
        return self._convert_to_embed_url(self.url)
    
    def get_watch_url(self):
        """Get the original watch URL for linking (not embedding)."""
        import re
        
        if not self.url:
            return None
        
        # If it's an embed URL, convert back to watch URL
        embed_match = re.search(r'/embed/([^?&]+)', self.url)
        if embed_match:
            video_id = embed_match.group(1)
            return f'https://www.youtube.com/watch?v={video_id}'
        
        # If it's already a watch URL, return as is
        if 'watch?v=' in self.url or 'youtu.be/' in self.url:
            return self.url
        
        # For other platforms, return the URL as is
        return self.url
    
    def __str__(self):
        return f"{self.media_type} for {self.story.title}"


class StoryAttachment(models.Model):
    """
    Junction model connecting stories to any other model via GenericForeignKey.
    Allows one story to relate to multiple objects with context.
    """
    story = models.ForeignKey(
        Story,
        on_delete=models.CASCADE,
        related_name="attachments"
    )
    
    # GenericForeignKey fields
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    attachment_context = models.CharField(
        max_length=100,
        blank=True,
        help_text="Context for why this story relates (e.g., 'learning_journey', 'breakthrough_moment')"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        # Prevent duplicate attachments
        unique_together = ['story', 'content_type', 'object_id']
    
    def __str__(self):
        return f"{self.story.title} → {self.content_object}"
