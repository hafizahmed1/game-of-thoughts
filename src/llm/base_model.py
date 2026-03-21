from abc import ABC, abstractmethod


class BaseModel(ABC):
    """
    Abstract LLM model interface.
    """

    name = "base_model"

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Generate model response from prompt.
        """
        pass