#!/usr/bin/env python3
"""Draw assets/og-image.png (1200x630) for link previews. Needs Pillow.

Run from the repository root: python3 scripts/make_og_image.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
W, H = 1200, 630
img = Image.new("RGB", (W, H), (20, 16, 15))
draw = ImageDraw.Draw(img)

# Signature gradient bar: #FD8957 -> #F56673 (55%) -> #FF5D8F
stops = [(0.0, (253, 137, 87)), (0.55, (245, 102, 115)), (1.0, (255, 93, 143))]
def colour(t):
    for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
        if t <= t1:
            f = (t - t0) / (t1 - t0)
            return tuple(round(a + (b - a) * f) for a, b in zip(c0, c1))
    return stops[-1][1]
for x in range(W):
    draw.line([(x, H - 14), (x, H)], fill=colour(x / (W - 1)))

logo = Image.open(ROOT / "assets" / "fulcrum-logo.png").convert("RGBA").resize((300, 300))
img.paste(logo, (64, 150), logo)

def font(size, bold=False):
    for path in ["/System/Library/Fonts/HelveticaNeue.ttc", "/System/Library/Fonts/Helvetica.ttc"]:
        try:
            return ImageFont.truetype(path, size, index=1 if bold else 0)
        except OSError:
            continue
    return ImageFont.load_default()

draw.text((400, 205), "Fulcrum Docs", font=font(84, True), fill=(255, 255, 255))
draw.text((404, 320), "How to use Fulcrum Mail, Calendar,", font=font(38), fill=(210, 208, 211))
draw.text((404, 370), "booking pages, Lyre and Fulcrum CRM", font=font(38), fill=(210, 208, 211))
draw.text((404, 450), "Part of Fulcrum Cortex, the AI execution layer", font=font(28), fill=(253, 137, 87))
img.save(ROOT / "assets" / "og-image.png", optimize=True)
print("wrote assets/og-image.png")
