"""Local benchmark runner for PintaAI image providers.

Usage from repository root:

    python backend/benchmark.py --provider qwen --model qwen-image-2.0-pro
    python backend/benchmark.py --provider seedream --model doubao-seedream-5-0-lite-260628 --ages 5 6
"""

import argparse
import base64
import csv
import mimetypes
import os
import sys
import time
from pathlib import Path
from typing import List, Optional

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.prompt_builder import build_prompt  # noqa: E402
from backend.providers import generate_image  # noqa: E402

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}


def iter_images(input_dir: Path, limit: Optional[int]) -> List[Path]:
    images = sorted([p for p in input_dir.rglob("*") if p.suffix.lower() in IMAGE_EXTENSIONS])
    if limit is not None:
        images = images[:limit]
    return images


def save_result(result, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if result.image_b64:
        output_path.write_bytes(base64.b64decode(result.image_b64))
        return
    if result.image_url:
        response = requests.get(result.image_url, timeout=120)
        response.raise_for_status()
        output_path.write_bytes(response.content)
        return
    raise RuntimeError("Provider returned neither image_b64 nor image_url")


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark PintaAI image providers locally.")
    parser.add_argument("--provider", required=True, choices=["openai", "qwen", "seedream", "zhipu"])
    parser.add_argument("--model", default=None, help="Provider model ID. Falls back to env/default.")
    parser.add_argument("--ages", nargs="+", default=["5", "6"], choices=["4", "5", "6"])
    parser.add_argument("--input-dir", default=str(ROOT / "benchmark" / "inputs"))
    parser.add_argument("--output-dir", default=str(ROOT / "benchmark" / "outputs"))
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--size", default="1024x1024")
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    images = iter_images(input_dir, args.limit)
    if not images:
        print(f"No input images found in {input_dir}")
        return

    benchmark_dir = ROOT / "benchmark"
    results_path = benchmark_dir / "results.csv"
    write_header = not results_path.exists()

    with results_path.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "provider",
                "model",
                "photo",
                "age",
                "output_path",
                "status",
                "latency_seconds",
                "error",
            ],
        )
        if write_header:
            writer.writeheader()

        for image_path in images:
            for age in args.ages:
                prompt = build_prompt(age=age)
                model_label = args.model or os.getenv("IMAGE_MODEL", "default")
                output_name = f"{image_path.stem}_age{age}.png"
                output_path = output_dir / f"{args.provider}_{model_label.replace('/', '_')}" / output_name

                started = time.perf_counter()
                try:
                    result = generate_image(
                        provider=args.provider,
                        prompt=prompt,
                        image_bytes=image_path.read_bytes(),
                        content_type=mimetypes.guess_type(image_path.name)[0] or "image/png",
                        model=args.model,
                        size=args.size,
                    )
                    save_result(result, output_path)
                    status = "ok"
                    error = ""
                    print(f"[OK] {args.provider} {model_label} {image_path.name} age {age}")
                except Exception as exc:
                    output_path = Path("")
                    status = "error"
                    error = str(exc).replace("\n", " ")[:500]
                    print(f"[ERROR] {image_path.name} age {age}: {error}")
                latency = round(time.perf_counter() - started, 2)
                writer.writerow(
                    {
                        "provider": args.provider,
                        "model": model_label,
                        "photo": image_path.name,
                        "age": age,
                        "output_path": str(output_path),
                        "status": status,
                        "latency_seconds": latency,
                        "error": error,
                    }
                )
                fh.flush()


if __name__ == "__main__":
    main()
