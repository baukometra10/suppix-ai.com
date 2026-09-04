"""Premium proximity overlay on real Live Map screenshot."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

base_path = os.path.join("assets", "livemap-screenshot-1.jpg")
out_path = os.path.join("assets", "livemap-proximity-on-screenshot.jpg")

base = Image.open(base_path).convert("RGBA")
W, H = base.size

# Soft dim so overlays read clearly without hiding the map
veil = Image.new("RGBA", (W, H), (5, 10, 18, 55))
composed = Image.alpha_composite(base, veil)

glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
draw_glow = ImageDraw.Draw(glow, "RGBA")
overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
draw = ImageDraw.Draw(overlay, "RGBA")

try:
    font_dist = ImageFont.truetype("arialbd.ttf", max(22, W // 36))
    font_name = ImageFont.truetype("arialbd.ttf", max(15, W // 58))
    font_meta = ImageFont.truetype("arial.ttf", max(12, W // 70))
    font_badge = ImageFont.truetype("arialbd.ttf", max(13, W // 68))
except OSError:
    font_dist = ImageFont.load_default()
    font_name = font_dist
    font_meta = font_dist
    font_badge = font_dist

# Cleaner pin layout (two clear pairs)
pins = [
    {"name": "A. Müller", "role": "vor Ort", "xy": (int(W * 0.40), int(H * 0.30)), "color": (64, 196, 255)},
    {"name": "S. Khan", "role": "vor Ort", "xy": (int(W * 0.58), int(H * 0.40)), "color": (64, 196, 255)},
    {"name": "Team 3", "role": "4 Personen", "xy": (int(W * 0.42), int(H * 0.66)), "color": (64, 196, 255)},
    {"name": "J. Weber", "role": "unterwegs", "xy": (int(W * 0.62), int(H * 0.74)), "color": (255, 176, 64)},
]


def rounded_label(d, xy, lines, fill, outline, fonts, pad=10, radius=12):
    x, y = xy
    widths, heights = [], []
    for text, font, _ in lines:
        b = d.textbbox((0, 0), text, font=font)
        widths.append(b[2] - b[0])
        heights.append(b[3] - b[1])
    tw = max(widths)
    th = sum(heights) + 4 * (len(lines) - 1)
    box = [x - tw / 2 - pad, y, x + tw / 2 + pad, y + th + pad * 2]
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=2)
    cy = y + pad
    for i, (text, font, color) in enumerate(lines):
        b = d.textbbox((0, 0), text, font=font)
        w = b[2] - b[0]
        d.text((x - w / 2, cy), text, fill=color, font=font)
        cy += heights[i] + 4
    return box


def proximity(p1, p2, meters):
    x1, y1 = p1
    x2, y2 = p2
    # soft glow line
    draw_glow.line([(x1, y1), (x2, y2)], fill=(80, 230, 210, 55), width=14)
    draw.line([(x1, y1), (x2, y2)], fill=(120, 240, 220, 230), width=3)
    # dashed feel with small white ticks
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    text = f"{meters} m"
    b = draw.textbbox((0, 0), text, font=font_dist)
    tw, th = b[2] - b[0], b[3] - b[1]
    pad_x, pad_y = 14, 8
    box = [mx - tw / 2 - pad_x, my - th / 2 - pad_y, mx + tw / 2 + pad_x, my + th / 2 + pad_y]
    draw.rounded_rectangle(box, radius=999, fill=(8, 14, 24, 235), outline=(110, 240, 220, 255), width=2)
    draw.text((mx - tw / 2, my - th / 2 - 1), text, fill=(160, 255, 235), font=font_dist)


proximity(pins[0]["xy"], pins[1]["xy"], 10)
proximity(pins[2]["xy"], pins[3]["xy"], 45)

for p in pins:
    x, y = p["xy"]
    c = p["color"]
    # outer glow
    for r, a in ((28, 35), (18, 70)):
        draw_glow.ellipse((x - r, y - r, x + r, y + r), fill=(*c, a))
    # pin
    draw.ellipse((x - 11, y - 11, x + 11, y + 11), fill=(255, 255, 255, 255))
    draw.ellipse((x - 8, y - 8, x + 8, y + 8), fill=(*c, 255))
    # card below
    rounded_label(
        draw,
        (x, y + 16),
        [
            (p["name"], font_name, (240, 246, 255)),
            (p["role"], font_meta, (150, 175, 200)),
        ],
        fill=(8, 14, 24, 230),
        outline=(*c, 180),
        fonts=None,
        pad=9,
        radius=10,
    )

# Top demo chip — minimal
chip = "Demo · Nähe"
b = draw.textbbox((0, 0), chip, font=font_badge)
tw, th = b[2] - b[0], b[3] - b[1]
bx, by = int(W * 0.09), int(H * 0.13)
draw.rounded_rectangle(
    (bx, by, bx + tw + 28, by + th + 16),
    radius=999,
    fill=(8, 14, 24, 220),
    outline=(110, 240, 220, 220),
    width=2,
)
# live dot
draw.ellipse((bx + 10, by + 10, bx + 18, by + 18), fill=(80, 230, 210, 255))
draw.text((bx + 24, by + 7), chip, fill=(210, 245, 240), font=font_badge)

# Bottom caption bar — cleaner, full width inset
caption = "Beispiel-Nähe  ·  X ist 10 m von Y  ·  noch ohne echte Mitarbeiter"
b = draw.textbbox((0, 0), caption, font=font_meta)
tw, th = b[2] - b[0], b[3] - b[1]
bar_w = min(W - 48, tw + 48)
hx = (W - bar_w) / 2
hy = H - 46
draw.rounded_rectangle(
    (hx, hy - 6, hx + bar_w, hy + th + 14),
    radius=14,
    fill=(8, 14, 24, 220),
    outline=(70, 120, 160, 140),
    width=1,
)
draw.text(((W - tw) / 2, hy + 2), caption, fill=(185, 205, 225), font=font_meta)

glow_blur = glow.filter(ImageFilter.GaussianBlur(radius=6))
composed = Image.alpha_composite(composed, glow_blur)
composed = Image.alpha_composite(composed, overlay)
composed.convert("RGB").save(out_path, "JPEG", quality=90, optimize=True)
print("saved", out_path, os.path.getsize(out_path), f"{W}x{H}")
