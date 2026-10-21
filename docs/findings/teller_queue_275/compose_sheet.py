"""One package's look shots as a two-column sheet: the given stations, each frame scaled to 800 x 450 and labelled with
the sheet's label and its station's name.

    python docs/findings/teller_queue_275/compose_sheet.py <frames dir> <out.jpg> <prefix> <label> station [...]

``prefix`` is what look_shots put before a station's name ("" in the level's own light, "INSPECT_studio_" in the
inspection light). Writes a JPG and stops.
"""
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFont

d, out, prefix, label = sys.argv[1:5]
stations = sys.argv[5:]
W, H, PAD, HEAD = 800, 450, 6, 22
rows = (len(stations) + 1) // 2
font = ImageFont.load_default()
sheet = Image.new("RGB", (2 * W + 3 * PAD, rows * (H + HEAD + PAD) + PAD), (24, 24, 24))
draw = ImageDraw.Draw(sheet)
for i, st in enumerate(stations):
    p = pathlib.Path(d) / (prefix + st + ".png")
    if not p.is_file():
        raise SystemExit("FAIL: no frame %s" % p)
    x = PAD + (i % 2) * (W + PAD)
    y = PAD + (i // 2) * (H + HEAD + PAD)
    draw.text((x + 4, y + 4), "%s -- %s" % (label, st), fill=(235, 235, 235), font=font)
    sheet.paste(Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS), (x, y + HEAD))
sheet.save(out, quality=88)
print("wrote", out, sheet.size)
