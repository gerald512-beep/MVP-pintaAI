import importlib
import os
from typing import Optional

from .base import ProviderResult

PROVIDER_MODULES = {
    "openai": "openai_provider",
    "qwen": "qwen_provider",
    "seedream": "seedream_provider",
    "zhipu": "zhipu_provider",
}


def generate_image(
    provider: Optional[str],
    prompt: str,
    image_bytes: bytes,
    content_type: str,
    model: Optional[str] = None,
    size: str = "1024x1024",
) -> ProviderResult:
    provider = (provider or os.getenv("IMAGE_PROVIDER", "openai")).strip().lower()
    module_name = PROVIDER_MODULES.get(provider)
    if not module_name:
        raise ValueError(f"Unsupported provider '{provider}'. Choose one of: {', '.join(PROVIDER_MODULES)}")

    module = importlib.import_module(f".{module_name}", package=__name__)
    return module.generate(
        prompt=prompt,
        image_bytes=image_bytes,
        content_type=content_type,
        model=model or os.getenv("IMAGE_MODEL") or None,
        size=size,
    )
