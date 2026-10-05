import base64
import os
import mimetypes
from typing import Optional

import requests

from .base import ProviderResult


def generate(
    prompt: str,
    image_bytes: bytes,
    content_type: str,
    model: Optional[str] = None,
    size: str = "1024x1024",
) -> ProviderResult:
    api_key = os.getenv("ARK_API_KEY")
    if not api_key:
        raise RuntimeError("ARK_API_KEY is not set")

    endpoint = os.getenv("ARK_ENDPOINT", "https://ark.cn-beijing.volces.com/api/v3/images/generations")
    mime = content_type or mimetypes.guess_type("image.png")[0] or "image/png"
    encoded = base64.b64encode(image_bytes).decode("utf-8")

    payload = {
        "model": model or os.getenv("SEEDREAM_MODEL", "doubao-seedream-5-0-lite-260628"),
        "prompt": prompt,
        "image": f"data:{mime};base64,{encoded}",
        "size": size,
        "response_format": "url",
        "watermark": False,
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
        raise RuntimeError(f"Ark returned non-JSON response: {response.text[:500]}")

    if response.status_code != 200:
        raise RuntimeError(f"Ark error {response.status_code}: {data}")

    items = data.get("data", [])
    if not items:
        raise RuntimeError(f"Ark response missing image data: {data}")

    first = items[0]
    if first.get("error"):
        raise RuntimeError(f"Ark image error: {first['error']}")

    return ProviderResult(
        image_b64=first.get("b64_json"),
        image_url=first.get("url"),
        prompt_used=prompt,
        raw=data,
    )
