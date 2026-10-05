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
) -> str:
    cfg = resolve_config(age, regions, thickness, line_style, background)
    return PROMPT_TEMPLATE.format(age=age, **cfg)
