import os
from dotenv import load_dotenv
from google import genai

load_dotenv()


def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY missing in .env")

    return genai.Client(api_key=api_key)


def get_model_name():
    return os.getenv("MODEL_NAME", "models/gemini-3.1-flash-lite-preview")


def generate_text(prompt: str):
    client = get_gemini_client()
    model = get_model_name()

    response = client.models.generate_content(
        model=model,
        contents=prompt
    )

    return response.text