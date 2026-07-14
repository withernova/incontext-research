#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Safely export local SVG figures to PNG using headless Chrome.

Why: macOS qlmanage thumbnails may crop/clip large SVGs. This script reads each
SVG's intrinsic width/height and asks Chrome to screenshot the full document.
No Python plotting/rendering dependency is required.
"""
from pathlib import Path
import re, subprocess, tempfile, shutil, os, sys

HERE = Path(__file__).resolve().parent
FIG = HERE / "figures"
OUT = FIG / "png_safe"
OUT.mkdir(parents=True, exist_ok=True)
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
if not CHROME.exists():
    raise SystemExit("Google Chrome not found; cannot export PNG safely.")

def svg_size(svg_text):
    m = re.search(r'<svg[^>]*\bwidth="([0-9.]+)"[^>]*\bheight="([0-9.]+)"', svg_text)
    if m:
        return int(float(m.group(1))), int(float(m.group(2)))
    m = re.search(r'<svg[^>]*\bviewBox="[^"]*?\s+([0-9.]+)\s+([0-9.]+)"', svg_text)
    if m:
        return int(float(m.group(1))), int(float(m.group(2)))
    return 1400, 900

for svg in sorted(FIG.glob("fig*.svg")):
    text = svg.read_text(encoding="utf-8")
    w, h = svg_size(text)
    scale = 2  # high resolution, no crop
    out = OUT / (svg.stem + ".png")
    html = f"""<!doctype html>
<html><head><meta charset='utf-8'>
<style>
html, body {{ margin:0; padding:0; width:{w}px; height:{h}px; overflow:hidden; background:white; }}
img {{ display:block; width:{w}px; height:{h}px; }}
</style></head>
<body><img src='{svg.resolve().as_uri()}'></body></html>"""
    with tempfile.TemporaryDirectory() as td:
        hp = Path(td) / "page.html"
        hp.write_text(html, encoding="utf-8")
        cmd = [
            str(CHROME), "--headless=new", "--disable-gpu", "--hide-scrollbars",
            f"--window-size={w},{h}", f"--force-device-scale-factor={scale}",
            f"--screenshot={out}", hp.resolve().as_uri(),
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"wrote {out} ({w*scale}x{h*scale})")

# also make preview HTML pointing to safe PNGs
idx = ["<html><head><meta charset='utf-8'><title>Safe PNG figures</title></head><body style='font-family:sans-serif'>", "<h1>Safe PNG exports</h1>"]
for p in sorted(OUT.glob('fig*.png')):
    idx.append(f"<h2>{p.name}</h2><img src='{p.name}' style='max-width:100%;border:1px solid #ddd'>")
idx.append("</body></html>")
(OUT / "index.html").write_text("\n".join(idx), encoding="utf-8")
print("preview", OUT / "index.html")
