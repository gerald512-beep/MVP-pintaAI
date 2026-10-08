import base64
import os
import mimetypes
from typing import Optional

from io import BytesIO

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

    if size:
        requested_size = size.replace("x", "*")
    else:
        try:
            from PIL import Image
            from math import log

            with Image.open(BytesIO(image_bytes)) as im:
                src_w, src_h = im.size
            target_ratio = src_w / src_h
            best_error = float("inf")
            best_size = "1024*1024"
            for width in range(512, 2049, 16):
                for height in range(512, 2049, 16):
                    ratio_error = abs(log((width / height) / target_ratio))
                    area_error = abs((width * height) / (1024 * 1024) - 1)
                    # Ratio fidelity is the priority; keep output near the model's normal 1K quality.
                    score = ratio_error * 100 + area_error * 0.2
                    if score < best_error:
                        best_error = score
                        best_size = f"{width}*{height}"
            requested_size = best_size
        except Exception:
            requested_size = "1024*1024"

    payload = {
        "model": model or os.getenv("QWEN_MODEL", "qwen-image-edit-plus"),
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
            "size": requested_size,
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
