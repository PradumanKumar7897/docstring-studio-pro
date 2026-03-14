from .models import DocIssue


def validate_docstring_text(docstring: str, line: int = 1, symbol: str = None, kind: str = None):
    issues = []

    if not docstring or not docstring.strip():
        issues.append(DocIssue("B000", "Docstring is empty.", line, symbol, kind))
        return issues

    doc = docstring.strip()

    if not (doc.startswith('"""') and doc.endswith('"""')):
        issues.append(DocIssue("B001", 'Docstring should use triple double quotes (""").', line, symbol, kind))

    return issues
