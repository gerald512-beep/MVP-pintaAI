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
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise RuntimeError("DASHSCOPE_API_KEY is not set")

    base_url = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope-intl.aliyuncs.com/api/v1").rstrip("/")
    endpoint = os.getenv(
        "DASHSCOPE_ENDPOINT",
        f"{base_url}/services/aigc/multimodal-generation/generation",
    )

    mime = content_type or mimetypes.guess_type("image.png")[0] or "image/png"
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    image_data_url = f"data:{mime};base64,{encoded}"

    payload = {
        "model": model or os.getenv("QWEN_MODEL", "qwen-image-2.0-pro"),
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"image": image_data_url},
                        {"text": prompt},
                    ],
                }
            ]
        },
        "parameters": {
            "n": 1,
            "negative_prompt": " ",
            "prompt_extend": True,
            "watermark": False,
            "size": size.replace("x", "*"),
        },
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
        raise RuntimeError(f"DashScope returned non-JSON response: {response.text[:500]}")

    if response.status_code != 200 or data.get("code"):
        raise RuntimeError(f"DashScope error {response.status_code}: {data}")

    choices = data.get("output", {}).get("choices", [])
    if not choices:
        raise RuntimeError(f"DashScope response missing choices: {data}")

    content = choices[0].get("message", {}).get("content", [])
    for item in content:
        url = item.get("image")
        if url:
            return ProviderResult(image_url=url, prompt_used=prompt, raw=data)

    raise RuntimeError(f"DashScope response missing image URL: {data}")
