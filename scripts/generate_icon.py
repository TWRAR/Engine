"""One-off generator for assets/icon.png, assets/icon.ico, assets/logo.png.

Run with: python scripts/generate_icon.py
Requires Pillow (dev-only; not a runtime dependency of the app itself).
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).resolve().parent.parent / "assets"
ASSETS.mkdir(exist_ok=True)

RED = (220, 38, 38, 255)        # red-600, the project's icon/acronym color
RED_LIGHT = (248, 113, 113, 255)  # red-400, the tagline color
WHITE = (255, 255, 255, 255)

FONT_BOLD = r"C:\Windows\Fonts\arialbd.ttf"
FONT_REGULAR = r"C:\Windows\Fonts\arial.ttf"


def draw_glyph(size: int) -> Image.Image:
    """Cursor (recording clicks) + play triangle (replaying them), white on red."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    radius = size * 0.22
    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=RED)

    # Cursor-arrow glyph, scaled to a unit box then mapped into the canvas.
    cursor_unit = [
        (0.28, 0.14), (0.28, 0.74), (0.44, 0.59),
        (0.54, 0.82), (0.64, 0.78), (0.53, 0.55), (0.74, 0.55),
    ]
    draw.polygon([(x * size, y * size) for x, y in cursor_unit], fill=WHITE)

    # Play triangle, standing in for "replay" next to the cursor's "record".
    play_unit = [(0.62, 0.14), (0.62, 0.38), (0.84, 0.26)]
    draw.polygon([(x * size, y * size) for x, y in play_unit], fill=WHITE)

    return img


def draw_wordmark() -> Image.Image:
    width, height = 960, 260
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    icon_size = 220
    icon = draw_glyph(icon_size)
    icon_y = (height - icon_size) // 2
    img.paste(icon, (20, icon_y), icon)

    text_x = 20 + icon_size + 30

    acronym_font = ImageFont.truetype(FONT_BOLD, 128)
    acronym = "TWRAR"
    acronym_bbox = draw.textbbox((0, 0), acronym, font=acronym_font)
    acronym_top = icon_y + 6
    draw.text(
        (text_x, acronym_top - acronym_bbox[1]),
        acronym,
        font=acronym_font,
        fill=RED,
    )

    tagline_font = ImageFont.truetype(FONT_REGULAR, 38)
    tagline = "The Website Recorder And Replayer"
    tagline_top = acronym_top + (acronym_bbox[3] - acronym_bbox[1]) + 14
    draw.text(
        (text_x, tagline_top),
        tagline,
        font=tagline_font,
        fill=RED_LIGHT,
    )

    return img


def main() -> None:
    logo = draw_wordmark()
    logo.save(ASSETS / "logo.png")

    icon_sizes = [16, 24, 32, 48, 64, 128, 256]
    icon_base = draw_glyph(256)
    icon_base.save(ASSETS / "icon.png")
    icon_base.save(ASSETS / "icon.ico", sizes=[(s, s) for s in icon_sizes])

    print(f"Wrote {ASSETS / 'logo.png'}, {ASSETS / 'icon.png'}, {ASSETS / 'icon.ico'}")


if __name__ == "__main__":
    main()
