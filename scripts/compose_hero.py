#!/usr/bin/env python3
"""Compose the static README hero: typography + generated card photo."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
LEFT_SVG = ROOT / "assets/readme/hero-left.svg"
PHOTO = ROOT / "assets/readme/card.jpg"
OUTPUT = ROOT / "assets/readme/hero.png"
WIDTH, HEIGHT = 1200, 400
RADIUS = 28


def render_svg(svg: Path, png: Path) -> None:
    subprocess.run(
        ["sips", "-s", "format", "png", str(svg), "--out", str(png)],
        check=True,
        capture_output=True,
    )


def rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    return mask


def main() -> None:
    if not PHOTO.is_file():
        raise SystemExit(f"missing photo: {PHOTO}")

    with tempfile.TemporaryDirectory(prefix="hero-compose-") as tmp:
        left_png = Path(tmp) / "left.png"
        render_svg(LEFT_SVG, left_png)
        left = Image.open(left_png).convert("RGBA").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)

    photo = Image.open(PHOTO).convert("RGBA")
    # Cover the right panel, slightly taller than the canvas so the stack sits in frame.
    panel_w, panel_h = 620, HEIGHT
    scale = max(panel_w / photo.width, panel_h / photo.height)
    photo = photo.resize(
        (max(1, int(photo.width * scale)), max(1, int(photo.height * scale))),
        Image.Resampling.LANCZOS,
    )
    left_crop = max(0, (photo.width - panel_w) // 2 - 20)
    top_crop = max(0, (photo.height - panel_h) // 2)
    photo = photo.crop((left_crop, top_crop, left_crop + panel_w, top_crop + panel_h))

    fade = Image.new("L", (panel_w, panel_h), 255)
    fade_draw = ImageDraw.Draw(fade)
    for x in range(90):
        fade_draw.line([(x, 0), (x, panel_h)], fill=int(255 * (x / 90)))
    photo.putalpha(fade)

    canvas = Image.new("RGBA", (WIDTH, HEIGHT), (18, 20, 26, 255))
    canvas.alpha_composite(left, (0, 0))
    canvas.alpha_composite(photo, (WIDTH - panel_w, 0))
    canvas.putalpha(rounded_mask((WIDTH, HEIGHT), RADIUS))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(OUTPUT, "PNG", optimize=True)
    print(f"hero: {OUTPUT} ({OUTPUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
