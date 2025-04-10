from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications"""
    sender_name = serializers.CharField(source='sender.username', read_only=True, allow_null=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'sender', 'sender_name', 'notification_type',
            'title', 'message', 'is_read', 'related_object_type',
            'related_object_id', 'created_at'
        ]
        read_only_fields = ['recipient', 'sender', 'created_at']