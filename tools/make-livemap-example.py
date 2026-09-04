from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1200, 680
img = Image.new("RGB", (W, H), (7, 11, 20))
draw = ImageDraw.Draw(img, "RGBA")

for x in range(0, W, 40):
    draw.line([(x, 0), (x, H)], fill=(30, 50, 70, 70), width=1)
for y in range(0, H, 40):
    draw.line([(0, y), (W, y)], fill=(30, 50, 70, 70), width=1)

draw.rounded_rectangle(
    (80, 90, 520, 420),
    radius=24,
    outline=(94, 184, 232, 120),
    width=2,
    fill=(94, 184, 232, 18),
)
draw.rounded_rectangle(
    (560, 250, 1080, 560),
    radius=24,
    outline=(45, 212, 191, 110),
    width=2,
    fill=(45, 212, 191, 16),
)

pins = [
    ("A. Müller", (280, 250), (94, 184, 232)),
    ("S. Khan", (430, 310), (94, 184, 232)),
    ("Team 3", (760, 360), (94, 184, 232)),
    ("J. Weber", (900, 300), (245, 158, 11)),
]

try:
    font = ImageFont.truetype("arial.ttf", 18)
    font_b = ImageFont.truetype("arialbd.ttf", 20)
    font_title = ImageFont.truetype("arialbd.ttf", 28)
    font_small = ImageFont.truetype("arial.ttf", 15)
    font_m = ImageFont.truetype("arialbd.ttf", 24)
except OSError:
    font = ImageFont.load_default()
    font_b = font
    font_title = font
    font_small = font
    font_m = font


def dist_label(p1, p2, meters):
    x1, y1 = p1
    x2, y2 = p2
    draw.line([(x1, y1), (x2, y2)], fill=(94, 234, 212, 60), width=8)
    draw.line([(x1, y1), (x2, y2)], fill=(94, 234, 212, 210), width=3)
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    text = f"{meters} m"
    bbox = draw.textbbox((0, 0), text, font=font_m)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad = 10
    box = [
        mx - tw / 2 - pad,
        my - th / 2 - pad - 8,
        mx + tw / 2 + pad,
        my + th / 2 + pad - 8,
    ]
    draw.rounded_rectangle(
        box, radius=10, fill=(7, 11, 20, 235), outline=(94, 234, 212, 220), width=2
    )
    draw.text((mx - tw / 2, my - th / 2 - 8), text, fill=(94, 234, 212), font=font_m)


dist_label(pins[0][1], pins[1][1], 10)
dist_label(pins[2][1], pins[3][1], 45)

for name, (x, y), color in pins:
    draw.ellipse((x - 18, y - 18, x + 18, y + 18), outline=(*color, 90), width=2)
    draw.ellipse((x - 8, y - 8, x + 8, y + 8), fill=color, outline=(255, 255, 255), width=2)
    bbox = draw.textbbox((0, 0), name, font=font_b)
    tw = bbox[2] - bbox[0]
    card = [x - tw / 2 - 12, y + 16, x + tw / 2 + 12, y + 48]
    draw.rounded_rectangle(
        card, radius=8, fill=(7, 11, 20, 235), outline=(94, 184, 232, 160), width=1
    )
    draw.text((x - tw / 2, y + 24), name, fill=(232, 238, 247), font=font_b)

draw.rounded_rectangle(
    (24, 18, W - 24, 70),
    radius=12,
    fill=(17, 24, 39, 240),
    outline=(94, 184, 232, 80),
    width=1,
)
draw.text((48, 30), "Beispiel · Nähe zwischen Mitarbeitern", fill=(232, 238, 247), font=font_title)
draw.rounded_rectangle((W - 140, 30, W - 48, 58), radius=999, fill=(94, 234, 212))
draw.text((W - 118, 35), "LIVE", fill=(7, 11, 20), font=font_b)

draw.rounded_rectangle(
    (40, H - 88, 580, H - 28),
    radius=12,
    fill=(17, 24, 39, 230),
    outline=(94, 184, 232, 90),
    width=1,
)
draw.text(
    (58, H - 72),
    "Linie = Distanz in Echtzeit  ·  Beispiel: X ist 10 m von Y",
    fill=(139, 155, 179),
    font=font_small,
)

chips = ["Haversine", "Bounding Box", "Spatial Index"]
cx = W - 520
for i, c in enumerate(chips):
    x0 = cx + i * 165
    draw.rounded_rectangle(
        (x0, H - 78, x0 + 150, H - 38),
        radius=10,
        fill=(15, 28, 44, 240),
        outline=(94, 184, 232, 120),
        width=1,
    )
    bbox = draw.textbbox((0, 0), c, font=font_small)
    tw = bbox[2] - bbox[0]
    draw.text((x0 + (150 - tw) / 2, H - 68), c, fill=(94, 184, 232), font=font_small)

draw.text((100, 105), "Zone A · Bau Süd", fill=(160, 190, 210), font=font_small)
draw.text((580, 265), "Zone B · Tor", fill=(160, 200, 190), font=font_small)

out = os.path.join("assets", "livemap-proximity-example.jpg")
img.convert("RGB").save(out, "JPEG", quality=88, optimize=True)
print("saved", out, os.path.getsize(out))
