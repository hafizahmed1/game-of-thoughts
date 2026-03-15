import os
from dotenv import load_dotenv

load_dotenv()

_gemini_client = None
_groq_client = None


def get_provider():
    return os.getenv("LLM_PROVIDER", "gemini").strip().lower()


def get_model_name():
    provider = get_provider()

    if provider == "groq":
        return os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile")

    return os.getenv("MODEL_NAME", "models/gemini-3.1-flash-lite-preview")


# -----------------------------
# Gemini
# -----------------------------
def get_gemini_client():
    global _gemini_client

    if _gemini_client is None:
        from google import genai

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY missing in .env")

        _gemini_client = genai.Client(api_key=api_key)

    return _gemini_client


def generate_text_gemini(prompt: str) -> str:
    client = get_gemini_client()
    model = get_model_name()

    response = client.models.generate_content(
        model=model,
        contents=prompt
    )

    return response.text


# -----------------------------
# Groq / Meta Llama
# -----------------------------
def get_groq_client():
    global _groq_client

    if _groq_client is None:
        from groq import Groq

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY missing in .env")

        _groq_client = Groq(api_key=api_key)

    return _groq_client


def generate_text_groq(prompt: str) -> str:
    client = get_groq_client()
    model = get_model_name()

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    return completion.choices[0].message.content


# -----------------------------
# Unified entry point
# -----------------------------
def generate_text(prompt: str) -> str:
    provider = get_provider()

    if provider == "groq":
        return generate_text_groq(prompt)

    if provider == "gemini":
        return generate_text_gemini(prompt)

    raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")