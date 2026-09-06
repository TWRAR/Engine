"""One-off generator for assets/icon.png, assets/icon.ico, assets/logo.png.

Run with: python scripts/generate_icon.py
Requires Pillow (dev-only; not a runtime dependency of the app itself).
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

ASSETS = Path(__file__).resolve().parent.parent / "assets"
ASSETS.mkdir(exist_ok=True)

BG = (15, 23, 42, 255)       # slate-900
ACCENT = (45, 212, 191, 255)  # teal-400
WHITE = (241, 245, 249, 255)  # slate-100


def draw_glyph(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    radius = size * 0.22
    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=BG)

    # Cursor-arrow glyph, scaled to a unit box then mapped into the canvas.
    unit = [
        (0.30, 0.16), (0.30, 0.74), (0.45, 0.60),
        (0.55, 0.82), (0.64, 0.78), (0.54, 0.56), (0.74, 0.56),
    ]
    points = [(x * size, y * size) for x, y in unit]
    draw.polygon(points, fill=WHITE)

    # Small "recording" dot near the cursor tip, to hint at automation/capture.
    dot_r = size * 0.075
    cx, cy = size * 0.76, size * 0.24
    draw.ellipse([cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r], fill=ACCENT)

    return img


def main() -> None:
    logo = draw_glyph(1024)
    logo.save(ASSETS / "logo.png")

    icon_sizes = [16, 24, 32, 48, 64, 128, 256]
    icon_base = draw_glyph(256)
    icon_base.save(ASSETS / "icon.png")
    icon_base.save(ASSETS / "icon.ico", sizes=[(s, s) for s in icon_sizes])

    print(f"Wrote {ASSETS / 'logo.png'}, {ASSETS / 'icon.png'}, {ASSETS / 'icon.ico'}")


if __name__ == "__main__":
    main()
