import json
import openai
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings

# Set up OpenAI API key
openai.api_key = settings.OPENAI_API_KEY

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = 'chat_room'
        self.room_group_name = f'chat_{self.room_name}'

        # Join WebSocket group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave WebSocket group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Receive message from WebSocket
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send the message to OpenAI and get the response
        ai_response = await self.get_ai_response(message)

        # Send the AI response to WebSocket
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': ai_response
            }
        )

    async def chat_message(self, event):
        # Send the message to WebSocket
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))

    # Function to interact with OpenAI API (updated method)
    async def get_ai_response(self, user_message):
        try:
            # Correct method: Use openai.ChatCompletion.create()
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Correct model name (can also use 'gpt-4' if you have access)
                messages=[{"role": "user", "content": user_message}],
                max_completion_tokens=250,  # Use 'max_completion_tokens' instead of 'max_tokens'
                temperature=1  # Adjust for creativity
            )
            # Return the response text
            return response['choices'][0]['message']['content'].strip()
        except Exception as e:
            return f"Error: {str(e)}"
