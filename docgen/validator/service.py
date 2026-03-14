import ast
from collections import defaultdict
from typing import Optional

from .config import ValidationConfig
from .models import DocIssue
from .pep257_basic import validate_docstring_text


def validate_project_code(code: str, cfg: Optional[ValidationConfig] = None) -> dict:
    cfg = cfg or ValidationConfig()
    grouped = defaultdict(list)

    try:
        tree = ast.parse(code)

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                symbol = node.name
                kind = "class" if isinstance(node, ast.ClassDef) else "function"
                ds = ast.get_docstring(node)

                if ds is None:
                    grouped[symbol].append(
                        DocIssue("B000", "Missing docstring.", node.lineno, symbol, kind)
                    )
                else:
                    wrapped = f'"""{ds}"""'
                    grouped[symbol].extend(
                        validate_docstring_text(wrapped, node.lineno, symbol, kind)
                    )
    except Exception:
        pass

    return dict(grouped)
