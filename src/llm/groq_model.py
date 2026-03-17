import time
from typing import Optional

from groq import Groq
from src.llm.base_model import BaseModel


class GroqModel(BaseModel):

    name = "groq"

    def __init__(self, api_key: str, model_name: str, max_retries: int = 3):
        self.client = Groq(api_key=api_key)
        self.model_name = model_name
        self.max_retries = max_retries

    def _extract_text(self, response) -> Optional[str]:

        try:
            if (
                response
                and response.choices
                and response.choices[0].message
                and response.choices[0].message.content
            ):
                return response.choices[0].message.content.strip()
        except Exception:
            pass

        return None

    def generate(self, prompt: str) -> str:

        for attempt in range(self.max_retries):

            try:

                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                )

                text = self._extract_text(response)

                if text:
                    return text

                print("Empty Groq response. Retrying...")

            except Exception as e:

                error_msg = str(e)

                if "rate limit" in error_msg.lower():
                    print("Groq rate limit hit. Waiting 30 seconds...")
                    time.sleep(30)
                    continue

                if "timeout" in error_msg.lower():
                    print("Groq timeout. Retrying...")
                    time.sleep(10)
                    continue

                print(f"Groq error: {error_msg}")

                if attempt == self.max_retries - 1:
                    return "INVALID_RESPONSE"

        return "INVALID_RESPONSE"