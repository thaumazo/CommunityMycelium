from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
import hashlib
import hmac

class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False)
    is_email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)  # Users are inactive until email is verified
    full_name = models.CharField(max_length=255, blank=True)

    # Remove first_name and last_name from the model
    first_name = None
    last_name = None

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.full_name

    def is_admin(self):
        return self.groups.filter(name="Admin").exists()

    def is_editor(self):
        return self.groups.filter(name="Editor").exists()

    def is_viewer(self):
        return self.groups.filter(name="Viewer").exists()

    @property
    def role(self):
        if self.is_superuser:
            return "Admin"
        if self.groups.filter(name="Admin").exists():
            return "Admin"
        if self.groups.filter(name="Editor").exists():
            return "Editor"
        if self.groups.filter(name="Viewer").exists():
            return "Viewer"
        return "No Role"

    def get_role(self):
        if self.is_superuser:
            return "Admin"
        if self.groups.filter(name="Admin").exists():
            return "Admin"
        if self.groups.filter(name="Editor").exists():
            return "Editor"
        if self.groups.filter(name="Viewer").exists():
            return "Viewer"
        return "No Role"

class EmailVerification(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    @classmethod
    def create_verification(cls, user):
        # Create a unique token using HMAC
        timestamp = str(timezone.now().timestamp())
        message = f"{user.email}{timestamp}".encode()
        token = hmac.new(
            settings.EMAIL_VERIFICATION_SALT.encode(),
            message,
            hashlib.sha256
        ).hexdigest()
        
        # Delete any existing unverified tokens for this user
        cls.objects.filter(user=user, is_verified=False).delete()
        
        # Create new verification
        return cls.objects.create(user=user, token=token)

    def is_expired(self):
        expiry_date = self.created_at + timedelta(days=settings.EMAIL_VERIFICATION_EXPIRY_DAYS)
        return timezone.now() > expiry_date

    def verify(self):
        if not self.is_expired():
            self.is_verified = True
            self.save()
            self.user.is_active = True
            self.user.is_email_verified = True
            self.user.save()
            return True
        return False
