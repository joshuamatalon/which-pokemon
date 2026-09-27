"""Builds web/img/og.png: a simple 1200x630 title card on paper colour, no Pokemon artwork,
for the Open Graph preview when the link is pasted into iMessage."""
from PIL import Image, ImageDraw, ImageFont
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "web", "img", "og.png")

PAPER = (247, 245, 240)
INK = (26, 26, 26)
MUTED = (95, 95, 95)
ACCENT = (176, 66, 26)

W, H = 1200, 630
img = Image.new("RGB", (W, H), PAPER)
draw = ImageDraw.Draw(img)

font_paths = [
    r"C:\Windows\Fonts\segoeuib.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
]
title_font = None
for p in font_paths:
    if os.path.exists(p):
        title_font = ImageFont.truetype(p, 84)
        break
if title_font is None:
    title_font = ImageFont.load_default()

sub_paths = [r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf"]
sub_font = None
for p in sub_paths:
    if os.path.exists(p):
        sub_font = ImageFont.truetype(p, 34)
        break
if sub_font is None:
    sub_font = ImageFont.load_default()

# thin rule near top
draw.rectangle([0, 0, W, 6], fill=ACCENT)

title_lines = ["Which Pokémon", "are you?"]
y = 190
for line in title_lines:
    bbox = draw.textbbox((0, 0), line, font=title_font)
    w = bbox[2] - bbox[0]
    draw.text(((W - w) / 2, y), line, font=title_font, fill=INK)
    y += 100

sub = "A short, positive quiz for the family"
bbox = draw.textbbox((0, 0), sub, font=sub_font)
w = bbox[2] - bbox[0]
draw.text(((W - w) / 2, y + 20), sub, font=sub_font, fill=MUTED)

img.save(OUT)
print(f"Wrote {OUT} {img.size}")
