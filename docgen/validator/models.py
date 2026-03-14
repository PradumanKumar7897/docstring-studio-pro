from dataclasses import dataclass
from typing import Optional


@dataclass
class DocIssue:
    """
    Represents one docstring validation issue.
    """
    code: str
    message: str
    line: int
    symbol: Optional[str] = None
    kind: Optional[str] = None  # function/class/module
