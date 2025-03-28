from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="organizations"
    )
