import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    return genai.Client(api_key=api_key)

def get_model_name():
    return os.getenv("MODEL_NAME", "models/gemini-3.1-flash-lite-preview")