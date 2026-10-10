"""Lay frames out as a captioned sheet.

    python sheet.py out.png cols "caption one=path1.png" "caption two=path2.png" ...

Each frame is scaled to 800 px wide, captioned in a bar under it, laid out `cols` across.
"""
import sys

from PIL import Image, ImageDraw, ImageFont

out, cols = sys.argv[1], int(sys.argv[2])
items = []
for arg in sys.argv[3:]:
    cap, _, path = arg.rpartition("=")
    items.append((cap, Image.open(path).convert("RGB")))
W = 800
frames = []
for cap, im in items:
    h = round(im.height * W / im.width)
    frames.append((cap, im.resize((W, h), Image.LANCZOS)))
H = max(f.height for _, f in frames)
BAR = 34
rows = (len(frames) + cols - 1) // cols
sheet = Image.new("RGB", (cols * W, rows * (H + BAR)), (24, 24, 24))
try:
    font = ImageFont.truetype("arial.ttf", 20)
except OSError:
    font = ImageFont.load_default()
d = ImageDraw.Draw(sheet)
for i, (cap, f) in enumerate(frames):
    x, y = (i % cols) * W, (i // cols) * (H + BAR)
    sheet.paste(f, (x, y))
    d.text((x + 10, y + H + 6), cap, fill=(235, 235, 235), font=font)
sheet.save(out)
print(out, sheet.size)
