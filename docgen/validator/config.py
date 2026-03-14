from dataclasses import dataclass, field


@dataclass
class ValidationConfig:
    ignore_codes: list[str] = field(default_factory=list)
    select_codes: list[str] = field(default_factory=list)
