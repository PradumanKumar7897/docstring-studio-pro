import re
from docgen.templates.registry import get_template


def _guess_summary(name: str, item_type="function") -> str:
    if item_type == "class":
        return f"{name} class."

    words = re.sub(r"[_]+", " ", name).strip()

    if words.startswith("get "):
        return f"Get {words[4:]}."
    if words.startswith("set "):
        return f"Set {words[4:]}."
    if words.startswith("is "):
        return f"Check whether {words[3:]}."
    if words.startswith("create "):
        return f"Create {words[7:]}."
    if words.startswith("build "):
        return f"Build {words[6:]}."
    if words.startswith("generate "):
        return f"Generate {words[9:]}."

    return f"{words.capitalize()}."


def generate_docstring(
    name: str,
    args: list[dict],
    returns: str | None = None,
    style: str = "google",
    item_type: str = "function",
) -> str:
    """
    Generate docstring using template system.
    """
    summary = _guess_summary(name, item_type=item_type)
    template = get_template(style)

    if item_type == "class":
        return template.render_class(name=name, summary=summary)

    return template.render_function(
        name=name,
        summary=summary,
        args=args,
        returns=returns or "Any",
    )
