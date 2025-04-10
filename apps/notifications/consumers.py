import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        # Reject connection if user is not authenticated
        if self.user.is_anonymous:
            await self.close()
            return
        
        # Set user's notification group name
        self.notification_group_name = f'notifications_{self.user.id}'
        
        # Join user's notification group
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave user's notification group
        if hasattr(self, 'notification_group_name'):
            await self.channel_layer.group_discard(
                self.notification_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """
        Receive message from WebSocket.
        Currently handles marking notifications as read.
        """
        data = json.loads(text_data)
        action = data.get('action')
        
        if action == 'mark_read':
            notification_id = data.get('notification_id')
            if notification_id:
                success = await self.mark_notification_read(notification_id)
                await self.send(text_data=json.dumps({
                    'action': 'mark_read_response',
                    'notification_id': notification_id,
                    'success': success
                }))
    
    async def notification_message(self, event):
        """
        Receive notification from notification group and send to WebSocket.
        """
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event['content']))
    
    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Mark a notification as read"""
        from .models import Notification
        try:
            notification = Notification.objects.get(
                id=notification_id,
                recipient=self.user
            )
            notification.mark_as_read()
            return True
        except Notification.DoesNotExist:
            return False