from django.db import models
from django.conf import settings

class Notification(models.Model):
    """Model for user notifications"""
    NOTIFICATION_TYPES = (
        ('system', 'System Notification'),
        ('activity', 'Activity Update'),
        ('alert', 'Alert'),
        ('message', 'Message'),
        ('recommendation', 'Recommendation'),
    )
    
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_notifications'
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    related_object_type = models.CharField(max_length=50, blank=True, null=True)
    related_object_id = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type}: {self.title} (to {self.recipient.username})"
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.save()