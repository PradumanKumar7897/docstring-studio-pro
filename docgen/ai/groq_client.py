from openai import OpenAI
from .exceptions import AIProviderError


def groq_generate(prompt, cfg):
    if not cfg.groq_key:
        raise AIProviderError("Groq API key missing")

    client = OpenAI(
        api_key=cfg.groq_key,
        base_url="https://api.groq.com/openai/v1",
    )

    try:
        response = client.chat.completions.create(
            model=cfg.resolve_model("groq"),
            messages=[{"role": "user", "content": prompt}],
            temperature=cfg.temperature,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        raise AIProviderError(str(e))