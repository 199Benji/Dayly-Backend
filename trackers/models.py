from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class Tracker(models.Model):
    # Link to your custom User profile
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='trackers'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    platform = models.CharField(max_length=50, blank=True, null=True)
    
    # Dashboard metrics
    total_score = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"

class Log(models.Model):
    tracker = models.ForeignKey(Tracker, on_delete=models.CASCADE, related_name='logs')
    date = models.DateField()
    
    # Category 1: Digital Proof
    content_link = models.URLField(blank=True, null=True)
    
    # Category 2: Visual Proof
    proof_image = models.ImageField(upload_to='logs/proof/', blank=True, null=True)
    
    # Verification Status
    is_verified = models.BooleanField(default=False)
    verification_message = models.CharField(max_length=255, blank=True, null=True)
    
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('tracker', 'date')

    def __str__(self):
        return f"{self.tracker.title} Log on {self.date}"