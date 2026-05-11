from abc import ABC, abstractmethod

class ILLMProvider(ABC):
    @abstractmethod
    def generate_response(self, system_prompt: str, user_prompt: str) -> str: ...
    
    @abstractmethod
    def summarize_text(self, text: str) -> str: ...