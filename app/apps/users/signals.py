from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import User, UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Create UserProfile
        UserProfile.objects.create(user=instance)

        # Add to viewer group by default
        viewer_group, _ = Group.objects.get_or_create(name="viewer")
        instance.groups.add(viewer_group)
