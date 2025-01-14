import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, Message
from django.contrib.auth.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # Verify room exists and user is participant
        if not await self.verify_room_access():
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    @database_sync_to_async
    def verify_room_access(self):
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            return room.participants.filter(id=self.user.id).exists()
        except ChatRoom.DoesNotExist:
            return False

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        
        # Save message to database
        await self.save_message(message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.user.username
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender']
        }))

    @database_sync_to_async
    def save_message(self, message):
        room = ChatRoom.objects.get(id=self.room_id)
        Message.objects.create(
            room=room,
            sender=self.user,
            content=message
        )