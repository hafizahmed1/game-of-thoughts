from __future__ import annotations

SUPPORTED_MODELS = [
    "llama-3.1-8b-instant",
    "qwen/qwen3-32b",
]

ACTIVE_MODELS = [
    "llama-3.1-8b-instant",
    "qwen/qwen3-32b",
]

DEFAULT_GAMES = [
    "tictactoe",
    "connect_four",
]

PROVIDER_BY_MODEL = {
    "llama-3.1-8b-instant": "groq",
    "qwen/qwen3-32b": "groq",
}


def is_supported_model(model_name: str) -> bool:
    return model_name in SUPPORTED_MODELS


def get_provider(model_name: str) -> str:
    if model_name not in PROVIDER_BY_MODEL:
        raise ValueError(f"Unknown model: {model_name}")
    return PROVIDER_BY_MODEL[model_name]