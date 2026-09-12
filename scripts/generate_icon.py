"""One-off generator for assets/icon.png, assets/icon.ico, assets/logo.png.

Run with: python scripts/generate_icon.py
Requires Pillow (dev-only; not a runtime dependency of the app itself).
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).resolve().parent.parent / "assets"
ASSETS.mkdir(exist_ok=True)

# Sibling Website repo's assets/ - only used for favicon.ico, which is a
# Website-only asset that has no business living in this repo.
WEBSITE_ASSETS = Path(__file__).resolve().parent.parent.parent / "Website" / "assets"

RED = (220, 38, 38, 255)  # red-600 - icon, acronym, and tagline color
WHITE = (255, 255, 255, 255)

FONT_BOLD = r"C:\Windows\Fonts\arialbd.ttf"
FONT_REGULAR = r"C:\Windows\Fonts\arial.ttf"


WINDOW_ASPECT = 1.5  # width:height of the drawn browser window


def window_bounds(size: int) -> tuple[float, float, float, float]:
    """The drawn browser window's (x0, y0, x1, y1) within a `size`-square
    canvas: full width, vertically centered, short enough to be a
    WINDOW_ASPECT-ratio rectangle rather than a square."""
    x0, x1 = 0, size - 1
    w = x1 - x0
    h = w / WINDOW_ASPECT
    y0 = (size - h) / 2
    y1 = y0 + h
    return x0, y0, x1, y1


def draw_glyph(size: int) -> Image.Image:
    """A red browser window - a wide rectangle with slightly rounded
    corners (not a square), letterboxed within the square canvas - with a
    chrome bar of three tab-bar dots, and the recording dot, play triangle,
    and cursor centered below it, white on red."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    x0, y0, x1, y1 = window_bounds(size)
    w, h = x1 - x0, y1 - y0

    radius = h * 0.10
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=RED)

    # All interior marks are laid out on a square sub-region (side = h,
    # the window's shorter dimension) centered horizontally in the window,
    # so circles/triangles keep their true proportions instead of being
    # squashed to the wider aspect.
    sub = h
    sx0 = x0 + (w - sub) / 2
    sy0 = y0

    def px(fx: float) -> float:
        return sx0 + fx * sub

    def py(fy: float) -> float:
        return sy0 + fy * sub

    # Browser chrome: three tab-bar dots in the top-left mark the top ~20%
    # of the window as a title/tab bar, so the shape reads as a browser
    # window rather than a plain rectangle.
    chrome_dot_r = sub * 0.028
    chrome_dot_cy = py(0.10)
    for fx in (0.14, 0.24, 0.34):
        chrome_dot_cx = px(fx)
        draw.ellipse(
            [
                chrome_dot_cx - chrome_dot_r, chrome_dot_cy - chrome_dot_r,
                chrome_dot_cx + chrome_dot_r, chrome_dot_cy + chrome_dot_r,
            ],
            fill=WHITE,
        )

    # The recording dot, play triangle, and cursor, in a clean two-row grid
    # below the chrome bar - no touching or crowding between any of the
    # three.
    dot_r = sub * 0.108
    dot_cx, dot_cy = px(0.29), py(0.377)
    draw.ellipse(
        [dot_cx - dot_r, dot_cy - dot_r, dot_cx + dot_r, dot_cy + dot_r],
        fill=WHITE,
    )

    play_unit = [(0.54, 0.260), (0.54, 0.494), (0.86, 0.377)]
    draw.polygon([(px(x), py(y)) for x, y in play_unit], fill=WHITE)

    cursor_unit = [
        (0.32, 0.557), (0.32, 0.920), (0.443, 0.833),
        (0.524, 0.970), (0.598, 0.945), (0.516, 0.807), (0.68, 0.807),
    ]
    draw.polygon([(px(x), py(y)) for x, y in cursor_unit], fill=WHITE)

    return img


def draw_wordmark() -> Image.Image:
    width, height = 960, 260
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    icon_size = 220
    icon = draw_glyph(icon_size)
    icon_y = (height - icon_size) // 2
    img.paste(icon, (20, icon_y), icon)

    # Align text to the icon's visible window, not the padded square it's
    # drawn on (the window is letterboxed within that square).
    _, window_y0, _, _ = window_bounds(icon_size)

    text_x = 20 + icon_size + 30

    acronym_font = ImageFont.truetype(FONT_BOLD, 128)
    acronym = "TWRAR"
    acronym_bbox = draw.textbbox((0, 0), acronym, font=acronym_font)
    acronym_top = icon_y + window_y0 + 6
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

    icon_hires = draw_glyph(1024)
    icon_hires.save(ASSETS / "icon.icns")

    print(
        f"Wrote {ASSETS / 'logo.png'}, {ASSETS / 'icon.png'}, "
        f"{ASSETS / 'icon.ico'}, {ASSETS / 'icon.icns'}"
    )

    # favicon.ico isn't used by the Engine app itself - it's only for the
    # Website repo's <link rel="shortcut icon"> - so it's written straight
    # into the sibling Website checkout instead of this repo's assets/.
    if WEBSITE_ASSETS.is_dir():
        favicon_sizes = [16, 32, 48]
        icon_base.save(WEBSITE_ASSETS / "favicon.ico", sizes=[(s, s) for s in favicon_sizes])
        print(f"Wrote {WEBSITE_ASSETS / 'favicon.ico'}")
    else:
        print(f"Skipped favicon.ico - no sibling checkout at {WEBSITE_ASSETS}")

    print("Copy logo.png/icon.png into Website/assets/ too if they changed.")


if __name__ == "__main__":
    main()
