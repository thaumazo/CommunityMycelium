from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
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
