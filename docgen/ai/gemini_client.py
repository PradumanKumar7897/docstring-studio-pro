import google as genai
from .exceptions import AIProviderError


def gemini_generate(prompt, cfg):
    if not cfg.gemini_key:
        raise AIProviderError("Gemini API key missing")

    genai.configure(api_key=cfg.gemini_key)

    try:
        model = genai.GenerativeModel(cfg.resolve_model("gemini"))
        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        raise AIProviderError(str(e))