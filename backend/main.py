import base64
import logging
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .prompt_builder import AGE_CONFIG, build_prompt, resolve_config
from .providers import generate_image


load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="PintaAI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/prompt-preview")
def prompt_preview(
    age: str,
    regions: str = "",
    thickness: str = "",
    line_style: str = "",
    background: str = "",
):
    if age not in AGE_CONFIG:
        raise HTTPException(status_code=400, detail=f"Invalid age '{age}'")
    cfg = resolve_config(age, regions, thickness, line_style, background)
    prompt = build_prompt(age=age, **cfg)
    return {"prompt": prompt}


@app.post("/api/generate")
async def generate(
    age: str = Form(...),
    topic: str = Form(...),
    image: UploadFile = File(...),
    regions: str = Form(""),
    thickness: str = Form(""),
    line_style: str = Form(""),
    background: str = Form(""),
):
    logger.info("Received /api/generate — age=%s, topic=%s, filename=%s", age, topic, image.filename)

    if age not in AGE_CONFIG:
        raise HTTPException(status_code=400, detail=f"Invalid age '{age}'. Must be one of: {list(AGE_CONFIG.keys())}")

    cfg = resolve_config(age, regions, thickness, line_style, background)
    logger.info("Config used: %s", cfg)
    prompt = build_prompt(age=age, **cfg)
    logger.info("Assembled prompt:\n%s", prompt)

    image_bytes = await image.read()
    provider = os.getenv("IMAGE_PROVIDER", "openai")
    model = os.getenv("IMAGE_MODEL", "")
    logger.info("Calling provider=%s model=%s — image size=%d bytes", provider, model, len(image_bytes))

    try:
        result = generate_image(
            provider=provider,
            prompt=prompt,
            image_bytes=image_bytes,
            content_type=image.content_type or "image/png",
            model=model or None,
            size="1024x1024",
        )
        logger.info("%s API call succeeded", provider)
    except Exception as exc:
        logger.error("%s API call failed: %s", provider, exc)
        raise HTTPException(status_code=500, detail=f"Image generation failed with {provider}: {exc}")

    if not result.image_b64 and result.image_url:
        try:
            import requests

            remote = requests.get(result.image_url, timeout=120)
            remote.raise_for_status()
            result.image_b64 = base64.b64encode(remote.content).decode("utf-8")
        except Exception as exc:
            logger.error("Failed to download generated image: %s", exc)
            return {"image_url": result.image_url, "prompt_used": prompt}

    if not result.image_b64:
        raise HTTPException(status_code=500, detail="Provider returned no image")

    # Save original API output to backend/images/ for comparison
    images_dir = Path(__file__).parent / "images"
    images_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_path = images_dir / f"age{age}_{timestamp}.png"
    save_path.write_bytes(base64.b64decode(result.image_b64))
    logger.info("Saved original image to %s", save_path)

    logger.info("Generation successful — returning base64 image")
    return {"image_b64": result.image_b64, "image_url": result.image_url, "prompt_used": prompt}


# Serve built frontend — must be mounted AFTER API routes
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
