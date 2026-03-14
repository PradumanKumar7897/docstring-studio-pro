import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class AIConfig:
    provider: str = "auto"
    model: str | None = None
    temperature: float = 0.2
    max_tokens: int = 1024
    timeout: int = 60
    max_retries: int = 2

    openai_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    gemini_key: str = field(default_factory=lambda: os.getenv("GOOGLE_API_KEY", ""))
    groq_key: str = field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))

    def resolve_model(self, provider: str) -> str:
        defaults = {
            "openai": "gpt-4.1-mini",
            "gemini": "gemini-1.5-flash",
            "groq": "llama-3.1-8b-instant",
        }
        return self.model or defaults.get(provider)