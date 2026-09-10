"""One-off generator for assets/icon.png, assets/icon.ico, assets/logo.png.

Run with: python scripts/generate_icon.py
Requires Pillow (dev-only; not a runtime dependency of the app itself).
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).resolve().parent.parent / "assets"
ASSETS.mkdir(exist_ok=True)

RED = (220, 38, 38, 255)  # red-600 - icon, acronym, and tagline color
WHITE = (255, 255, 255, 255)

FONT_BOLD = r"C:\Windows\Fonts\arialbd.ttf"
FONT_REGULAR = r"C:\Windows\Fonts\arial.ttf"


def draw_glyph(size: int) -> Image.Image:
    """Cursor + recording dot (recording clicks) and a play triangle
    (replaying them), white on red."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    radius = size * 0.22
    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=RED)

    # Three even marks in a clean two-row grid: a recording dot and a play
    # triangle side by side on top, the cursor spanning the row below - no
    # touching or crowding between any of the three.
    dot_r = size * 0.12
    dot_cx, dot_cy = size * 0.29, size * 0.26
    draw.ellipse(
        [dot_cx - dot_r, dot_cy - dot_r, dot_cx + dot_r, dot_cy + dot_r],
        fill=WHITE,
    )

    play_unit = [(0.54, 0.13), (0.54, 0.39), (0.86, 0.26)]
    draw.polygon([(x * size, y * size) for x, y in play_unit], fill=WHITE)

    cursor_unit = [
        (0.32, 0.46), (0.32, 0.864), (0.443, 0.767),
        (0.524, 0.92), (0.598, 0.892), (0.516, 0.739), (0.68, 0.739),
    ]
    draw.polygon([(x * size, y * size) for x, y in cursor_unit], fill=WHITE)

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

    tagline_font = ImageFont.truetype(FONT_BOLD, 38)
    tagline = "The Website Recorder And Replayer"
    tagline_top = acronym_top + (acronym_bbox[3] - acronym_bbox[1]) + 14
    draw.text(
        (text_x, tagline_top),
        tagline,
        font=tagline_font,
        fill=RED,
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
