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
from openai import OpenAI

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

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

AGE_CONFIG = {
    "4": {
        "regions": "6 to 9 large enclosed shapes",
        "thickness": "2.5 to 3 pts — similar to regular crayon strokes",
        "line_style": "All lines rounded corners, no sharp angles",
        "background": "No background",
    },
    "5": {
        "regions": "9 to 15 large enclosed shapes",
        "thickness": "1.5 to 2.5 pts — similar to thick marker strokes",
        "line_style": "Most lines rounded, simple angles allowed",
        "background": "Simple background and floor based on the uploaded photo",
    },
    "6": {
        "regions": "16 or more enclosed shapes",
        "thickness": "1 to 1.5 pts — similar to fine marker or colored pencil strokes",
        "line_style": "Mix of rounded and angular lines",
        "background": "Multiple background elements and floor based on the uploaded photo",
    },
}

PROMPT_TEMPLATE = """Transform the uploaded photo into a printable children's coloring page.

Goal:
Create a simple black-and-white coloring-book illustration that clearly resembles the same animal in the photo.

Preserve these identity traits from the original animal.

0.[Age] Simplify the image for children ages {age} years old
1.[Regions] Reduce the animal into large rounded enclosed shapes, between {regions}.
2. Keep the pose, body, and distinctive features recognizable.
3.[Thickness] Use an outline thickness between {thickness}.
4. Use very few interior detail lines.
5. Keep large open white spaces for easy coloring.
6.[Line Style] {line_style}.
7.[Background] {background}.

Style requirements:
- Black line art only
- The complete animal — head, body, legs, and tail — must be fully visible and centered in the frame
- Minimum 10% white margin on all four sides (top, bottom, left, right)
- Do not zoom in or crop any part of the animal
- Printable worksheet style
- Child-friendly cartoon look
- All regions fully enclosed
- High clarity and clean composition

Do not include:
- People
- Shadows
- Gray tones
- Color
- Gradients
- Textures
- Crosshatching
- Sketch lines
- Open outlines
- Decorative borders

Important:
Keep the animal recognizable as the same subject from the photo, especially the fur or feathers, tail, and posture. Do not include any people."""


@app.get("/api/health")
def health():
    return {"status": "ok"}


def _resolve_config(age: str, regions: str, thickness: str, line_style: str, background: str) -> dict:
    """Use custom values if provided, otherwise fall back to AGE_CONFIG defaults."""
    defaults = AGE_CONFIG.get(age, {})
    return {
        "regions":    regions    or defaults.get("regions", ""),
        "thickness":  thickness  or defaults.get("thickness", ""),
        "line_style": line_style or defaults.get("line_style", ""),
        "background": background or defaults.get("background", ""),
    }


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
    cfg = _resolve_config(age, regions, thickness, line_style, background)
    prompt = PROMPT_TEMPLATE.format(age=age, **cfg)
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

    cfg = _resolve_config(age, regions, thickness, line_style, background)
    logger.info("Config used: %s", cfg)
    prompt = PROMPT_TEMPLATE.format(age=age, **cfg)
    logger.info("Assembled prompt:\n%s", prompt)

    image_bytes = await image.read()
    logger.info("Calling OpenAI gpt-image-1 edit endpoint — image size=%d bytes", len(image_bytes))

    try:
        response = client.images.edit(
            model="gpt-image-1",
            image=("photo.png", image_bytes, image.content_type or "image/png"),
            prompt=prompt,
            size="1024x1024",
            quality="medium",
        )
        logger.info("OpenAI API call succeeded")
    except Exception as exc:
        logger.error("OpenAI API call failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))

    image_b64 = response.data[0].b64_json
    if not image_b64:
        url = response.data[0].url
        logger.info("b64_json not in response, returning url instead")
        return {"image_url": url, "prompt_used": prompt}

    # Save original API output to backend/images/ for comparison
    images_dir = Path(__file__).parent / "images"
    images_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_path = images_dir / f"age{age}_{timestamp}.png"
    save_path.write_bytes(base64.b64decode(image_b64))
    logger.info("Saved original image to %s", save_path)

    logger.info("Generation successful — returning base64 image")
    return {"image_b64": image_b64, "prompt_used": prompt}


# Serve built frontend — must be mounted AFTER API routes
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
