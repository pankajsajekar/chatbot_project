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

    # Function to interact with OpenAI API (correct method)
    async def get_ai_response(self, user_message):
        try:
            # Define the prompt dynamically based on the models and fields
            prompt = f"""
Based on the following student management system, which handles the following models:

1. **Student**: Contains fields like `student_id`, `name`, `department`, `email`, `phone_number`, `gpa`, `status`.
2. **Attendance**: Contains fields like `student`, `course`, `date`, `status` (Present/Absent).
3. **Grade**: Contains fields like `student`, `course`, `marks_obtained`, `total_marks`, `exam_type`, `semester`.
4. **Performance**: Contains fields like `student`, `course`, `gpa`, `status` (Completed, Ongoing, Failed).
5. **Internship**: Contains fields like `student`, `company_name`, `role`, `start_date`, `end_date`, `description`.

The user query is: "{user_message}"

---

### Response Format:

When the user asks for **specific student details**, for example, "Show me details of Alexis Peterson", return the student information in **list format** with the following details:

- **Name**: Alexis Peterson
- **Student ID**: [Student ID]
- **Department**: [Department Name]
- **Email**: [Email Address]
- **Phone Number**: [Phone Number]
- **GPA**: [GPA]
- **Status**: [Active/Graduated/On Leave]
- **Enrollment Year**: [Year]
- **Graduation Year**: [Year]

If you can't find any specific data for the student, return an appropriate message, such as "Student not found."

Answer the following query about retrieving details of a specific student from the database and return the details in a structured format.

### Example:
- **Query**: "Show me details of Alexis Peterson"
- **Response**:
    - **Name**: Alexis Peterson
    - **Student ID**: S12345
    - **Department**: Computer Science
    - **Email**: alexis.peterson@example.com
    - **Phone Number**: +123456789
    - **GPA**: 3.8
    - **Status**: Active
    - **Enrollment Year**: 2022
    - **Graduation Year**: 2026

Please provide the details of the student based on the available data.

"""

            # Generate the response using OpenAI's GPT model
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Correct model name (use "gpt-3.5-turbo" or "gpt-4" if you have access)
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=150,  # Use 'max_completion_tokens' instead of 'max_tokens'
                temperature=1  # Adjust for creativity
            )
            
            # Return the response text
            return response['choices'][0]['message']['content'].strip()
        except Exception as e:
            return f"Error: {str(e)}"
