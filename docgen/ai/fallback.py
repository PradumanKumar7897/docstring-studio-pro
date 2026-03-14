# docgen/ai/fallback.py

import time
from .router import PROVIDERS
from .metrics import metrics
from .exceptions import AIProviderError


def execute_with_fallback(prompt: str, cfg, initial_provider: str):
    """
    Smart fallback system:
    1. Try selected provider
    2. If fails, try others sorted by score
    3. Record metrics
    """

    available_providers = list(PROVIDERS.keys())

    if initial_provider not in available_providers:
        raise AIProviderError(f"Unknown provider: {initial_provider}")

    tried = set()
    errors = []

    def try_provider(provider_name):
        start = time.time()
        try:
            result = PROVIDERS[provider_name](prompt, cfg)
            latency = time.time() - start
            metrics.record_success(provider_name, latency)
            return result
        except Exception as e:
            metrics.record_failure(provider_name)
            errors.append(f"{provider_name}: {str(e)}")
            return None

    # 1️⃣ Try selected provider first
    result = try_provider(initial_provider)
    if result:
        return result

    tried.add(initial_provider)

    # 2️⃣ Sort remaining providers by score
    scored_providers = sorted(
        [p for p in available_providers if p not in tried],
        key=lambda p: metrics.score_provider(p),
        reverse=True,
    )

    # 3️⃣ Try fallback providers
    for provider in scored_providers:
        result = try_provider(provider)
        if result:
            return result

    # 4️⃣ If all failed
    error_message = "All providers failed.\n\n" + "\n".join(errors)
    raise AIProviderError(error_message)