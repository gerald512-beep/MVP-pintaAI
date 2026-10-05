from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ProviderResult:
    image_b64: Optional[str] = None
    image_url: Optional[str] = None
    prompt_used: str = ""
    raw: dict = field(default_factory=dict)
