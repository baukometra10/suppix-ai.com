"""Overlay proximity-line demo onto a real Live Map screenshot."""
from PIL import Image, ImageDraw, ImageFont
import os

base_path = os.path.join("assets", "livemap-screenshot-1.jpg")
out_path = os.path.join("assets", "livemap-proximity-on-screenshot.jpg")

base = Image.open(base_path).convert("RGBA")
W, H = base.size
overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
draw = ImageDraw.Draw(overlay, "RGBA")

try:
    font_m = ImageFont.truetype("arialbd.ttf", max(20, W // 40))
    font_b = ImageFont.truetype("arialbd.ttf", max(14, W // 65))
    font_s = ImageFont.truetype("arial.ttf", max(12, W // 75))
except OSError:
    font_m = ImageFont.load_default()
    font_b = font_m
    font_s = font_m

# Approximate pin positions on the Berlin screenshot (relative)
# Terminal-1 upper, Terminal-2 lower — place "employee" demos near terminals
pins = [
    ("A. Müller", (int(W * 0.42), int(H * 0.26)), (94, 184, 232)),
    ("S. Khan", (int(W * 0.56), int(H * 0.38)), (94, 184, 232)),
    ("Team 3", (int(W * 0.48), int(H * 0.62)), (94, 184, 232)),
    ("J. Weber", (int(W * 0.58), int(H * 0.70)), (245, 158, 11)),
]


def draw_distance(p1, p2, meters):
    x1, y1 = p1
    x2, y2 = p2
    draw.line([(x1, y1), (x2, y2)], fill=(94, 234, 212, 70), width=8)
    draw.line([(x1, y1), (x2, y2)], fill=(94, 234, 212, 230), width=3)
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    text = f"{meters} m"
    bbox = draw.textbbox((0, 0), text, font=font_m)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad = 8
    box = [mx - tw / 2 - pad, my - th / 2 - pad, mx + tw / 2 + pad, my + th / 2 + pad]
    draw.rounded_rectangle(box, radius=8, fill=(7, 11, 20, 230), outline=(94, 234, 212, 230), width=2)
    draw.text((mx - tw / 2, my - th / 2), text, fill=(94, 234, 212), font=font_m)


draw_distance(pins[0][1], pins[1][1], 10)
draw_distance(pins[2][1], pins[3][1], 45)

for name, (x, y), color in pins:
    r = max(7, W // 90)
    draw.ellipse((x - r * 2, y - r * 2, x + r * 2, y + r * 2), outline=(*color, 100), width=2)
    draw.ellipse((x - r, y - r, x + r, y + r), fill=color, outline=(255, 255, 255, 255), width=2)
    bbox = draw.textbbox((0, 0), name, font=font_b)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    card = [x - tw / 2 - 8, y + r + 6, x + tw / 2 + 8, y + r + 6 + th + 10]
    draw.rounded_rectangle(card, radius=6, fill=(7, 11, 20, 230), outline=(94, 184, 232, 180), width=1)
    draw.text((x - tw / 2, y + r + 10), name, fill=(232, 238, 247), font=font_b)

# Demo badge top-left of map area (below browser chrome-ish)
badge = "Demo · Nähe (Beispiel)"
bbox = draw.textbbox((0, 0), badge, font=font_s)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
bx, by = int(W * 0.08), int(H * 0.14)
draw.rounded_rectangle(
    (bx, by, bx + tw + 20, by + th + 14),
    radius=8,
    fill=(7, 11, 20, 220),
    outline=(94, 234, 212, 200),
    width=1,
)
draw.text((bx + 10, by + 6), badge, fill=(94, 234, 212), font=font_s)

# Bottom hint
hint = "Beispiel: X ist 10 m von Y  ·  noch ohne echte Mitarbeiter"
bbox = draw.textbbox((0, 0), hint, font=font_s)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
hx = (W - tw) / 2
hy = H - th - 28
draw.rounded_rectangle(
    (hx - 14, hy - 8, hx + tw + 14, hy + th + 8),
    radius=10,
    fill=(7, 11, 20, 225),
    outline=(94, 184, 232, 120),
    width=1,
)
draw.text((hx, hy), hint, fill=(180, 200, 220), font=font_s)

result = Image.alpha_composite(base, overlay).convert("RGB")
result.save(out_path, "JPEG", quality=88, optimize=True)
print("saved", out_path, os.path.getsize(out_path))
