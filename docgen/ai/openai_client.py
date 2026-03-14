from openai import OpenAI
from .exceptions import AIProviderError


def openai_generate(prompt, cfg):
    if not cfg.openai_key:
        raise AIProviderError("OpenAI API key missing")

    client = OpenAI(api_key=cfg.openai_key)

    try:
        response = client.chat.completions.create(
            model=cfg.resolve_model("openai"),
            messages=[{"role": "user", "content": prompt}],
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        raise AIProviderError(str(e))