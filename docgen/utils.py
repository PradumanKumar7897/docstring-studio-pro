def clean_docstring_text(doc: str) -> str:
    """
    Normalize docstring content by removing outer quotes if present.
    """
    if not doc:
        return ""

    s = doc.strip()

    if (s.startswith('"""') and s.endswith('"""')) or (s.startswith("'''") and s.endswith("'''")):
        s = s[3:-3]

    return s.strip("\n")
