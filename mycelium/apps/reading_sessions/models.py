from django.db import models
from apps.students.models import Student

# Create your models here.

class ReadingSession(models.Model):
    student = models.ForeignKey(Student, related_name='reading_sessions', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    date = models.DateField()
    audio = models.FileField(upload_to='reading_sessions/audio/')

    def __str__(self):
        return f"{self.title} ({self.date})"
