import time
from src.llm.base_model import BaseModel

class GeminiModel(BaseModel):
    def __init__(self, client, model_name: str):
        self.client = client
        self.model_name = model_name

    def generate(self, prompt: str) -> str:
        # 1. Add a small delay to stay safe (e.g., 5 seconds between calls)
        # This prevents 429 errors during rapid loops
        time.sleep(5) 
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            return response.text.strip()
        except Exception as e:
            if "429" in str(e):
                print("Rate limit reached. Sleeping for 60 seconds...")
                time.sleep(60)
                return self.generate(prompt) # Recursive retry
            raise e