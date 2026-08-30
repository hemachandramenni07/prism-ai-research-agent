'''
This file basically gives all the Gemini models that your API key/project can access
'''

from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY")
)

print("Models available to your API key:\n")

for model in client.models.list():
    if "generateContent" in model.supported_actions:
        print(model.name)