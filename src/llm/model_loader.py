import os

from src.config import SUPPORTED_MODELS, get_provider
from src.llm.groq_model import GroqModel


def load_model(model_name: str):
    model_name = model_name.lower()

    if model_name not in SUPPORTED_MODELS:
        raise ValueError(
            f"Unsupported model: {model_name}. Supported: {SUPPORTED_MODELS}"
        )

    provider = get_provider(model_name)

    if provider == "groq":
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not set in .env")

        return GroqModel(api_key=api_key, model_name=model_name)

    raise ValueError(f"Unsupported provider: {provider}")