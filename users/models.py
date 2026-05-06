from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    NICHE_CHOICES = [
        ('WEB_DEV', 'Web Developer'),
        ('GRAPHIC_DESIGN', 'Graphic Designer'),
        ('CONTENT_CREATOR', 'Content Creator'),
        ('VIDEO_EDITOR', 'Video Editor'),
        ('OTHER', 'Other'),
    ]
    
    profession = models.CharField(
        max_length=50, 
        choices=NICHE_CHOICES, 
        default='OTHER',
        db_index=True
    )
    bio = models.TextField(max_length=500, blank=True)
    profile_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.username