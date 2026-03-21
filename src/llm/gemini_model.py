import time
from typing import Optional

from src.llm.base_model import BaseModel


class GeminiModel(BaseModel):

    name = "gemini"

    def __init__(self, client, model_name: str, max_retries: int = 3):
        self.client = client
        self.model_name = model_name
        self.max_retries = max_retries

    def _extract_text(self, response) -> Optional[str]:
        """
        Safely extract text from Gemini response.
        """
        try:
            if response and hasattr(response, "text") and response.text:
                return response.text.strip()
        except Exception:
            pass

        return None

    def generate(self, prompt: str) -> str:

        for attempt in range(self.max_retries):

            try:
                time.sleep(3)  # avoid rate limits

                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                )

                text = self._extract_text(response)

                if text:
                    return text

                print("Empty Gemini response. Retrying...")

            except Exception as e:

                error_msg = str(e)

                if "429" in error_msg:
                    print("Gemini rate limit reached. Waiting 60 seconds...")
                    time.sleep(60)
                    continue

                if "timeout" in error_msg.lower():
                    print("Gemini timeout. Retrying...")
                    time.sleep(10)
                    continue

                print(f"Gemini error: {error_msg}")

                if attempt == self.max_retries - 1:
                    return "INVALID_RESPONSE"

        return "INVALID_RESPONSE"