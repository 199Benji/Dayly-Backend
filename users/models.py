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
    
    # For OTP verification
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    #Accept same name
    display_name = models.CharField(max_length=255, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    # --- TRACKER MODEL ---
class UserPlatform(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="platforms")
    platform_name = models.CharField(max_length=50) # e.g., Facebook, X, LinkedIn
    handle = models.CharField(max_length=100) # Their social media handle
    link = models.URLField(blank=True) # Optional link to their profile

    def __str__(self):
        return f"{self.user.username} on {self.platform_name}"