# docgen/ai/service.py

from .config import AIConfig
from .router import PROVIDERS, auto_select
from .fallback import execute_with_fallback
from .utils import retry_with_backoff
from .exceptions import AIProviderError


def generate_docstring_ai(prompt: str, cfg: AIConfig):
    """
    Unified AI generation entry point.

    Flow:
    1. Resolve provider (auto or manual)
    2. Execute with smart fallback
    3. Apply retry with exponential backoff
    4. Return generated docstring

    Raises:
        AIProviderError if all providers fail
    """

    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    def process():
        # 1️⃣ Determine provider
        provider = cfg.provider

        if provider == "auto":
            provider = auto_select(cfg)

        if provider not in PROVIDERS:
            raise AIProviderError(f"Unknown provider: {provider}")

        # 2️⃣ Execute with smart fallback
        return execute_with_fallback(prompt, cfg, provider)

    # 3️⃣ Retry with exponential backoff
    try:
        return retry_with_backoff(process, cfg.max_retries)
    except Exception as e:
        raise AIProviderError(f"Generation failed after retries: {str(e)}")