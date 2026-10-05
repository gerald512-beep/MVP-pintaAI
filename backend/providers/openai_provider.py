import os
from typing import Optional

from openai import OpenAI

from .base import ProviderResult


def generate(
    prompt: str,
    image_bytes: bytes,
    content_type: str,
    model: Optional[str] = None,
    size: str = "1024x1024",
) -> ProviderResult:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    client = OpenAI(api_key=api_key)
    response = client.images.edit(
        model=model or os.getenv("OPENAI_MODEL", "gpt-image-1"),
        image=("input", image_bytes, content_type or "image/png"),
        prompt=prompt,
        size=size,
        quality=os.getenv("OPENAI_QUALITY", "medium"),
    )

    image_b64 = getattr(response.data[0], "b64_json", None)
    image_url = getattr(response.data[0], "url", None)
    return ProviderResult(image_b64=image_b64, image_url=image_url, prompt_used=prompt, raw=response.model_dump())
