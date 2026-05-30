#!/usr/bin/env python3
"""Convert all SVGs in article_diagrams/ to high-res PNGs using Chrome headless."""
import os
import re
import subprocess
import sys

SVG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "article_diagrams")
CHROME   = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SCALE    = 2   # 2× — SVG widths are 960-1200 px → PNGs will be 1920-2400 px


def svg_dimensions(path: str) -> tuple[int, int]:
    with open(path, encoding="utf-8") as f:
        head = f.read(512)
    w = re.search(r'<svg[^>]+width="(\d+)"', head)
    h = re.search(r'<svg[^>]+height="(\d+)"', head)
    return (int(w.group(1)), int(h.group(1))) if (w and h) else (960, 500)


def convert(svg_file: str) -> bool:
    svg_path = os.path.join(SVG_DIR, svg_file)
    png_name = svg_file.replace(".svg", ".png")
    png_path = os.path.join(SVG_DIR, png_name)

    w, h = svg_dimensions(svg_path)

    html = (
        f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<style>*{{margin:0;padding:0;box-sizing:border-box}}"
        f"body{{width:{w}px;height:{h}px;overflow:hidden;background:#0c0c1c}}"
        f"</style></head><body>"
        f"<img src='file://{svg_path}' width='{w}' height='{h}'>"
        f"</body></html>"
    )
    html_path = f"/tmp/_svgconv_{svg_file}.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    try:
        subprocess.run(
            [
                CHROME,
                "--headless=new",
                "--disable-gpu",
                "--no-sandbox",
                "--hide-scrollbars",
                "--disable-extensions",
                f"--window-size={w},{h}",
                f"--force-device-scale-factor={SCALE}",
                f"--screenshot={png_path}",
                f"file://{html_path}",
            ],
            capture_output=True,
            timeout=30,
        )
    finally:
        os.unlink(html_path)

    if os.path.exists(png_path):
        kb = os.path.getsize(png_path) // 1024
        print(f"  ✓  {png_name:<42}  {w*SCALE}×{h*SCALE} px  {kb} KB")
        return True
    else:
        print(f"  ✗  {png_name}  FAILED", file=sys.stderr)
        return False


if __name__ == "__main__":
    svgs = sorted(f for f in os.listdir(SVG_DIR) if f.endswith(".svg"))
    print(f"Converting {len(svgs)} SVGs at {SCALE}× scale …\n")
    ok = sum(convert(s) for s in svgs)
    print(f"\n{ok}/{len(svgs)} converted → {SVG_DIR}")
