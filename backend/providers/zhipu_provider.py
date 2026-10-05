import os
from typing import Optional

import requests

from .base import ProviderResult


def generate(
    prompt: str,
    image_bytes: bytes,
    content_type: str,
    model: Optional[str] = None,
    size: str = "1280x1280",
) -> ProviderResult:
    """Zhipu GLM/CogView currently exposes a text-to-image endpoint.

    It is included as a prompt-only comparison candidate; it does not receive
    the input photo in this benchmark.
    """
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        raise RuntimeError("ZHIPU_API_KEY is not set")

    endpoint = os.getenv("ZHIPU_ENDPOINT", "https://api.z.ai/api/paas/v4/images/generations")
    payload = {
        "model": model or os.getenv("ZHIPU_MODEL", "glm-image"),
        "prompt": prompt,
        "size": size.replace("*", "x"),
        "quality": os.getenv("ZHIPU_QUALITY", "standard"),
    }

    response = requests.post(
        endpoint,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        json=payload,
        timeout=300,
    )
    try:
        data = response.json()
    except ValueError:
        response.raise_for_status()
        raise RuntimeError(f"Zhipu returned non-JSON response: {response.text[:500]}")

    if response.status_code != 200:
        raise RuntimeError(f"Zhipu error {response.status_code}: {data}")

    items = data.get("data", [])
    if not items or not items[0].get("url"):
        raise RuntimeError(f"Zhipu response missing image URL: {data}")

    return ProviderResult(image_url=items[0]["url"], prompt_used=prompt, raw=data)
