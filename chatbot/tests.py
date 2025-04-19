from django.test import TestCase

# Create your tests here.
import openai
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",  # Correct model name
    messages=[{"role": "user", "content": "What is the current date?"}],
    max_tokens=150,
    temperature=0.7
)

print(response['choices'][0]['message']['content'])