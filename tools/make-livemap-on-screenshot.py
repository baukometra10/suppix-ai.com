"""Cinematic proximity overlay on real Live Map screenshot."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os
import math

base_path = os.path.join("assets", "livemap-screenshot-1.jpg")
out_path = os.path.join("assets", "livemap-proximity-on-screenshot.jpg")

src = Image.open(base_path).convert("RGBA")
sw, sh = src.size

# Crop away busy app chrome → map only, cinematic frame
top = int(sh * 0.145)
bottom = int(sh * 0.985)
left = int(sw * 0.01)
right = int(sw * 0.995)
base = src.crop((left, top, right, bottom))
W, H = base.size

# Slight contrast + cool tone for premium look
base_rgb = base.convert("RGB")
base_rgb = ImageEnhance.Contrast(base_rgb).enhance(1.08)
base_rgb = ImageEnhance.Color(base_rgb).enhance(0.92)
base = base_rgb.convert("RGBA")

# Soft center spotlight + edge vignette
vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
vd = ImageDraw.Draw(vignette, "RGBA")
for i in range(28):
    a = int(6 + i * 3.2)
    inset = i * 7
    vd.rectangle((inset, inset, W - inset, H - inset), outline=(4, 8, 16, a), width=8)
vignette = vignette.filter(ImageFilter.GaussianBlur(18))

# Frost competing UI chrome so the demo reads first
frost = Image.new("RGBA", (W, H), (0, 0, 0, 0))
fd = ImageDraw.Draw(frost, "RGBA")
# left: zoom + filter pills
fd.rounded_rectangle((4, 4, int(W * 0.38), int(H * 0.28)), radius=18, fill=(5, 9, 16, 210))
# right: Liste / Legende / Dichte / Alerts
fd.rounded_rectangle((int(W * 0.48), 2, W - 4, int(H * 0.20)), radius=18, fill=(5, 9, 16, 220))
# bottom-left floating control
fd.ellipse((2, H - 62, 58, H - 6), fill=(5, 9, 16, 180))
# attribution corner
fd.rounded_rectangle((W - 210, H - 28, W - 4, H - 4), radius=8, fill=(5, 9, 16, 160))
frost = frost.filter(ImageFilter.GaussianBlur(14))

# Extra gaussian blur of chrome regions for glass feel
blurred = base.filter(ImageFilter.GaussianBlur(7))
chrome_mask = Image.new("L", (W, H), 0)
cm = ImageDraw.Draw(chrome_mask)
cm.rounded_rectangle((4, 4, int(W * 0.38), int(H * 0.28)), radius=18, fill=220)
cm.rounded_rectangle((int(W * 0.48), 2, W - 4, int(H * 0.20)), radius=18, fill=230)
cm.ellipse((2, H - 62, 58, H - 6), fill=180)
chrome_mask = chrome_mask.filter(ImageFilter.GaussianBlur(12))
base = Image.composite(blurred, base, chrome_mask)

composed = Image.alpha_composite(base, frost)
composed = Image.alpha_composite(composed, Image.new("RGBA", (W, H), (6, 12, 22, 48)))
composed = Image.alpha_composite(composed, vignette)

glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
draw_glow = ImageDraw.Draw(glow, "RGBA")
overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
draw = ImageDraw.Draw(overlay, "RGBA")

def load_fonts():
    candidates = [
        ("segoeuib.ttf", "segoeui.ttf"),
        ("arialbd.ttf", "arial.ttf"),
        ("C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/segoeui.ttf"),
        ("C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf"),
    ]
    for bold, regular in candidates:
        try:
            return (
                ImageFont.truetype(bold, max(26, W // 30)),
                ImageFont.truetype(bold, max(16, W // 52)),
                ImageFont.truetype(regular, max(12, W // 68)),
                ImageFont.truetype(bold, max(13, W // 62)),
            )
        except OSError:
            continue
    d = ImageFont.load_default()
    return d, d, d, d


font_dist, font_name, font_meta, font_badge = load_fonts()

# Pins placed relative to cropped map (between terminals, readable spacing)
pins = [
    {"name": "A. Müller", "role": "vor Ort", "xy": (int(W * 0.34), int(H * 0.28)), "color": (72, 198, 255)},
    {"name": "S. Khan", "role": "vor Ort", "xy": (int(W * 0.55), int(H * 0.38)), "color": (72, 198, 255)},
    {"name": "Team 3", "role": "4 Personen", "xy": (int(W * 0.38), int(H * 0.68)), "color": (64, 214, 196)},
    {"name": "J. Weber", "role": "unterwegs", "xy": (int(W * 0.64), int(H * 0.76)), "color": (255, 178, 72)},
]


def draw_soft_line(p1, p2, color, width, alpha):
    x1, y1 = p1
    x2, y2 = p2
    draw_glow.line([(x1, y1), (x2, y2)], fill=(*color, alpha), width=width)


def proximity(p1, p2, meters, accent=(94, 236, 214)):
    x1, y1 = p1
    x2, y2 = p2
    # layered glow corridor
    draw_soft_line(p1, p2, accent, 22, 28)
    draw_soft_line(p1, p2, accent, 12, 55)
    draw.line([(x1, y1), (x2, y2)], fill=(*accent, 235), width=2)

    # midpoint distance pill
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    # nudge slightly perpendicular so text sits cleanly on line
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy) or 1
    nx, ny = -dy / length, dx / length
    mx += nx * 2
    my += ny * 2

    text = f"{meters} m"
    b = draw.textbbox((0, 0), text, font=font_dist)
    tw, th = b[2] - b[0], b[3] - b[1]
    pad_x, pad_y = 14, 7
    box = [mx - tw / 2 - pad_x, my - th / 2 - pad_y, mx + tw / 2 + pad_x, my + th / 2 + pad_y]
    draw_glow.rounded_rectangle(
        [box[0] - 3, box[1] - 3, box[2] + 3, box[3] + 3],
        radius=999,
        fill=(*accent, 36),
    )
    draw.rounded_rectangle(box, radius=999, fill=(7, 12, 20, 245), outline=(*accent, 200), width=1)
    draw.text((mx - tw / 2, my - th / 2 - 1), text, fill=(225, 255, 248), font=font_dist)


def pin_marker(p, label_above=False):
    x, y = p["xy"]
    c = p["color"]

    # soft pulse rings
    for r, a in ((36, 22), (24, 40), (16, 70)):
        draw_glow.ellipse((x - r, y - r, x + r, y + r), fill=(*c, a))

    # white ring + color core
    draw.ellipse((x - 12, y - 12, x + 12, y + 12), fill=(255, 255, 255, 255))
    draw.ellipse((x - 9, y - 9, x + 9, y + 9), fill=(*c, 255))
    draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(255, 255, 255, 230))

    # glass name label
    name, role = p["name"], p["role"]
    nb = draw.textbbox((0, 0), name, font=font_name)
    rb = draw.textbbox((0, 0), role, font=font_meta)
    nw, nh = nb[2] - nb[0], nb[3] - nb[1]
    rw, rh = rb[2] - rb[0], rb[3] - rb[1]
    pad_x, pad_y, gap = 12, 8, 3
    tw = max(nw, rw)
    th = nh + rh + gap
    bw = tw + pad_x * 2 + 14  # room for status dot
    bh = th + pad_y * 2

    if label_above:
        lx, ly = x - bw / 2, y - 18 - bh
    else:
        lx, ly = x - bw / 2, y + 16

    # keep on canvas
    lx = max(8, min(lx, W - bw - 8))
    ly = max(8, min(ly, H - bh - 8))

    box = [lx, ly, lx + bw, ly + bh]
    draw_glow.rounded_rectangle([box[0] - 2, box[1] - 2, box[2] + 2, box[3] + 2], radius=14, fill=(*c, 35))
    draw.rounded_rectangle(box, radius=12, fill=(8, 14, 24, 228), outline=(*c, 160), width=1)

    # status dot
    dx0, dy0 = lx + 12, ly + bh / 2
    draw.ellipse((dx0 - 4, dy0 - 4, dx0 + 4, dy0 + 4), fill=(*c, 255))

    tx = lx + 22
    draw.text((tx, ly + pad_y - 1), name, fill=(245, 248, 255), font=font_name)
    draw.text((tx, ly + pad_y + nh + gap - 1), role, fill=(150, 175, 198), font=font_meta)


proximity(pins[0]["xy"], pins[1]["xy"], 10)
proximity(pins[2]["xy"], pins[3]["xy"], 45, accent=(110, 220, 255))

pin_marker(pins[0], label_above=True)
pin_marker(pins[1], label_above=False)
pin_marker(pins[2], label_above=True)
pin_marker(pins[3], label_above=False)

# Minimal demo chip — top left, after chrome is softened
chip = "Demo · Nähe"
b = draw.textbbox((0, 0), chip, font=font_badge)
tw, th = b[2] - b[0], b[3] - b[1]
bx, by = 18, 18
chip_box = (bx, by, bx + tw + 36, by + th + 16)
draw_glow.rounded_rectangle(
    (chip_box[0] - 3, chip_box[1] - 3, chip_box[2] + 3, chip_box[3] + 3),
    radius=999,
    fill=(64, 214, 196, 45),
)
draw.rounded_rectangle(chip_box, radius=999, fill=(8, 14, 24, 230), outline=(94, 236, 214, 210), width=1)
draw.ellipse((bx + 12, by + 10, bx + 20, by + 18), fill=(94, 236, 214, 255))
draw.text((bx + 26, by + 7), chip, fill=(220, 250, 245), font=font_badge)

# Soft bottom caption — short & elegant
caption = "Nähe in Metern  ·  Demo ohne echte Mitarbeiter"
b = draw.textbbox((0, 0), caption, font=font_meta)
tw, th = b[2] - b[0], b[3] - b[1]
bar_w = min(W - 40, tw + 40)
hx = (W - bar_w) / 2
hy = H - 36
draw.rounded_rectangle(
    (hx, hy - 5, hx + bar_w, hy + th + 11),
    radius=12,
    fill=(8, 14, 24, 210),
    outline=(70, 110, 140, 90),
    width=1,
)
draw.text(((W - tw) / 2, hy + 1), caption, fill=(175, 198, 218), font=font_meta)

glow_blur = glow.filter(ImageFilter.GaussianBlur(radius=7))
composed = Image.alpha_composite(composed, glow_blur)
composed = Image.alpha_composite(composed, overlay)

# Final subtle sharpen of overlay by slight upsample→down for polish optional skip
out = composed.convert("RGB")
out = ImageEnhance.Sharpness(out).enhance(1.05)
out.save(out_path, "JPEG", quality=92, optimize=True)
print("saved", out_path, os.path.getsize(out_path), f"{W}x{H}")
