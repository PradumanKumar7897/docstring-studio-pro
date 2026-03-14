from .openai_client import openai_generate
from .gemini_client import gemini_generate
from .groq_client import groq_generate

# ── Provider Registry ─────────────────────────────────────────────────
PROVIDERS = {
    "openai": openai_generate,
    "gemini": gemini_generate,
    "groq":   groq_generate,
}

PROVIDER_PRIORITY = ["openai", "gemini", "groq"]


# ── Auto Selection ────────────────────────────────────────────────────
def auto_select(cfg) -> str:
    """Return the first provider that has an API key configured.

    Args:
        cfg: AIConfig instance.

    Returns:
        Provider name string.

    Raises:
        Exception: If no API keys are found.
    """
    key_map = {
        "openai": getattr(cfg, "openai_key", None),
        "gemini": getattr(cfg, "gemini_key", None),
        "groq":   getattr(cfg, "groq_key",   None),
    }
    for provider in PROVIDER_PRIORITY:
        if key_map.get(provider):
            return provider

    raise Exception(
        "No API keys configured. Set OPENAI_API_KEY, GEMINI_API_KEY, "
        "or GROQ_API_KEY in your .env file."
    )


# ── Main Router ───────────────────────────────────────────────────────
def route_request(prompt: str, cfg) -> str:
    """Route a generation request to the correct AI provider.

    Args:
        prompt: Docstring generation prompt.
        cfg:    AIConfig with provider name, keys, and settings.

    Returns:
        Generated docstring string from the chosen provider.

    Raises:
        ValueError: If provider name is not registered.
        Exception:  If no API keys are available in auto mode.
    """
    provider = cfg.provider

    if provider == "auto":
        provider = auto_select(cfg)

    generate_fn = PROVIDERS.get(provider)

    if generate_fn is None:
        raise ValueError(
            f"Unknown provider: '{provider}'. "
            f"Available: {list(PROVIDERS.keys())}"
        )

    return generate_fn(prompt, cfg)


# ── Helpers ───────────────────────────────────────────────────────────
def list_providers() -> list:
    """Return all registered provider names."""
    return list(PROVIDERS.keys())


def is_valid_provider(name: str) -> bool:
    """Check if a provider name is registered (including 'auto')."""
    return name in PROVIDERS or name == "auto"