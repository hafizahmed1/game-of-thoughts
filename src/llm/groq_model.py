from __future__ import annotations

from groq import Groq

from src.llm.base_model import BaseModel


class GroqModel(BaseModel):
    name = "groq"

    def __init__(self, api_key: str, model_name: str):
        self.client = Groq(api_key=api_key)
        self.model_name = model_name

    def generate(self, prompt: str) -> str:
        try:
            request_kwargs = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
            }

            # Qwen-specific: disable thinking / reasoning output
            if self.model_name == "qwen/qwen3-32b":
                request_kwargs["reasoning_effort"] = "none"
                request_kwargs["reasoning_format"] = "hidden"

            completion = self.client.chat.completions.create(**request_kwargs)

        except Exception as e:
            raise RuntimeError(f"Groq API error ({self.model_name}): {e}")

        if not completion or not completion.choices:
            raise ValueError(f"No response from Groq model: {self.model_name}")

        message = completion.choices[0].message
        if message is None:
            raise ValueError(f"No message returned from Groq model: {self.model_name}")

        content = message.content
        if content is None:
            raise ValueError(f"Empty content from Groq model: {self.model_name}")

        if not isinstance(content, str):
            content = str(content)

        return content.strip()