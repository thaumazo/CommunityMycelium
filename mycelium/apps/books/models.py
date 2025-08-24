from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from apps.acl.models import ObjectPermission

User = get_user_model()

CATEGORY_CHOICES = [
    ('Fiction', 'Fiction'),
    ('Nonfiction', 'Nonfiction'),
]

class Book(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    level = models.CharField(max_length=1)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    writing_prompt = models.TextField()
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="books"
    )
    permissions = GenericRelation(ObjectPermission)

    def __str__(self):
        return self.title

    class Meta:
        permissions = [
            ("delegate_book", "Can delegate book"),
        ]

class Content(models.Model):
    book = models.ForeignKey(Book, related_name='contents', on_delete=models.CASCADE)
    page = models.IntegerField()
    text = models.TextField()

class ComprehensionWithin(models.Model):
    book = models.ForeignKey(Book, related_name='comprehension_within', on_delete=models.CASCADE)
    question = models.TextField()

class ComprehensionAbout(models.Model):
    book = models.ForeignKey(Book, related_name='comprehension_about', on_delete=models.CASCADE)
    question = models.TextField()