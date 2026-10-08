from typing import Dict

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
- Match the uploaded photo's aspect ratio, orientation, and overall framing; preserve the original crop
- Black line art only
- Keep the animal recognizable and avoid turning a portrait into a full body drawing
- Preserve exactly what is visible in the uploaded photo (for example, head only, head and shoulders, or full body); do not invent hidden body parts
- Keep the pose, face, body parts, fur/feathers, clothing or distinctive features recognizable
- Keep the original composition and visible subject proportions as closely as possible
- Zoom out if needed so the entire visible animal and scene fit comfortably
- Minimum 10% white margin on all four sides (top, bottom, left, right)
- Do not zoom in or crop any part of the animal
- Make the coloring page simple enough for the selected age while preserving the reference photo’s framing
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


MYSELF_PROMPT_TEMPLATE = """Transform the uploaded photo into a printable children's coloring page.

Goal:
Create a simple black-and-white coloring-book illustration that clearly resembles the same person in the photo.

Preserve these identity traits from the original person.

0.[Age] Simplify the image for children ages {age} years old
1.[Regions] Reduce the person into large rounded enclosed shapes, between {regions}.
2. Keep the pose, clothing, face, and distinctive features recognizable.
3.[Thickness] Use an outline thickness between {thickness}.
4. Use very few interior detail lines.
5. Keep large open white spaces for easy coloring.
6.[Line Style] {line_style}.
7.[Background] {background}.

Style requirements:
- Match the uploaded photo's aspect ratio, orientation, and overall framing; preserve the original crop
- Black line art only
- Keep the person recognizable and avoid turning the portrait into an animal, baby, mascot, or caricature
- Preserve exactly what is visible in the uploaded photo (for example, head and shoulders); do not invent hidden body parts
- Keep the visible clothing, face, hairstyle, expression, pose, and subject proportions recognizable
- Keep the original composition and framing as closely as possible
- Preserve the source image's natural crop rather than inventing body parts that are not visible
- Minimum 10% white margin on all four sides (top, bottom, left, right)
- Do not zoom in or crop any part of the person
- Printable worksheet style
- Child-friendly cartoon look
- All regions fully enclosed
- High clarity and clean composition

Do not include:
- Additional people
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
Keep the person recognizable as the same subject from the photo, especially the face, hair, clothing, and posture. Do not include additional people."""


def resolve_config(
    age: str,
    regions: str = "",
    thickness: str = "",
    line_style: str = "",
    background: str = "",
) -> Dict[str, str]:
    defaults = AGE_CONFIG.get(age, {})
    return {
        "regions": regions or defaults.get("regions", ""),
        "thickness": thickness or defaults.get("thickness", ""),
        "line_style": line_style or defaults.get("line_style", ""),
        "background": background or defaults.get("background", ""),
    }


def build_prompt(
    age: str,
    regions: str = "",
    thickness: str = "",
    line_style: str = "",
    background: str = "",
    topic: str = "animal",
) -> str:
    cfg = resolve_config(age, regions, thickness, line_style, background)
    if topic == "myself":
        return MYSELF_PROMPT_TEMPLATE.format(age=age, **cfg)
    return PROMPT_TEMPLATE.format(age=age, **cfg)
