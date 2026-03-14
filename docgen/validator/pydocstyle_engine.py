from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Optional

from pydocstyle import check

from .config import ValidationConfig
from .models import DocIssue


def _passes_filters(code: str, cfg: ValidationConfig) -> bool:
    if cfg.select_codes and code not in cfg.select_codes:
        return False
    if cfg.ignore_codes and code in cfg.ignore_codes:
        return False
    return True


def validate_file(filepath: str, cfg: Optional[ValidationConfig] = None) -> list[DocIssue]:
    cfg = cfg or ValidationConfig()
    filepath = str(Path(filepath).resolve())

    issues: list[DocIssue] = []

    for err in check([filepath]):
        if not _passes_filters(err.code, cfg):
            continue

        issues.append(
            DocIssue(
                code=err.code,
                message=err.message,
                line=err.line,
                symbol=getattr(err, "definition", None),
                kind=None,
            )
        )

    return issues


def validate_code_string(code: str, cfg: Optional[ValidationConfig] = None) -> list[DocIssue]:
    """
    Validates code without needing a real file.
    We write it to a temp .py file and run pydocstyle on it.
    """
    cfg = cfg or ValidationConfig()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "temp_code.py"
        tmp_path.write_text(code, encoding="utf-8")

        return validate_file(str(tmp_path), cfg)
