#!/usr/bin/env python3
"""Render hero.svg keyframes with sips and assemble a GitHub-safe GIF."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SVG = ROOT / "assets/readme/hero.svg"
GIF = ROOT / "assets/readme/hero.gif"

ET.register_namespace("", "http://www.w3.org/2000/svg")

# Progressive reveal. Last composition must match the first for a clean loop.
STAGES = [
    ["card-slug", "card-title", "card-meta", "layer-answer", "layer-example", "layer-followups"],
    ["card-meta", "layer-answer", "layer-example", "layer-followups"],
    ["layer-answer", "layer-example", "layer-followups"],
    ["layer-example", "layer-followups"],
    ["layer-followups"],
    [],
]

DURATIONS_MS = [220, 220, 220, 220, 220, 1800, 180, 180, 180, 180, 220]


def strip_ids(svg_text: str, hidden: list[str]) -> str:
    root = ET.fromstring(svg_text)
    hidden_set = set(hidden)
    for parent in root.iter():
        for child in list(parent):
            if child.attrib.get("id") in hidden_set:
                parent.remove(child)
    return ET.tostring(root, encoding="unicode")


def render_png(svg_path: Path, png_path: Path) -> None:
    subprocess.run(
        ["sips", "-s", "format", "png", str(svg_path), "--out", str(png_path)],
        check=True,
        capture_output=True,
    )


def main() -> None:
    source = SVG.read_text(encoding="utf-8")
    hidden_sequence = STAGES + list(reversed(STAGES[:-1]))
    if len(hidden_sequence) != len(DURATIONS_MS):
        raise SystemExit("stage count and duration count must match")

    with tempfile.TemporaryDirectory(prefix="hero-gif-") as tmp:
        tmp_path = Path(tmp)
        frames: list[Image.Image] = []
        preview_dir = Path("/tmp/hero-gif-frames")
        if preview_dir.exists():
            shutil.rmtree(preview_dir)
        preview_dir.mkdir(parents=True)
        for index, hidden in enumerate(hidden_sequence):
            frame_svg = tmp_path / f"frame-{index:02d}.svg"
            frame_png = tmp_path / f"frame-{index:02d}.png"
            frame_svg.write_text(strip_ids(source, hidden), encoding="utf-8")
            render_png(frame_svg, frame_png)
            shutil.copy(frame_png, preview_dir / f"frame-{index:02d}.png")
            frames.append(Image.open(frame_png).convert("P", palette=Image.ADAPTIVE, colors=128))

        GIF.parent.mkdir(parents=True, exist_ok=True)
        frames[0].save(
            GIF,
            save_all=True,
            append_images=frames[1:],
            duration=DURATIONS_MS,
            loop=0,
            optimize=True,
            disposal=2,
        )

    size_mb = GIF.stat().st_size / (1024 * 1024)
    print(f"GIF: {GIF} ({size_mb:.2f} MB, {len(frames)} frames)")
    if size_mb > 2.0:
        raise SystemExit("GIF exceeds 2 MB budget")


if __name__ == "__main__":
    if not shutil.which("sips"):
        raise SystemExit("sips is required to rasterize the SVG")
    main()
