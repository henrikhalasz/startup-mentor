import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Create a client for the Gemini model
from google.generativeai.types import GenerationConfig

# This will be used to create GenerativeModel instances
client = genai