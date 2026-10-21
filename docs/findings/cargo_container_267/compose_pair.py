"""Two packages' look shots side by side, one row a station: the BEFORE frame left, the AFTER frame right, each scaled
to 800 x 450 and labelled with its side's label and the station's name.

    python docs/findings/cargo_container_267/compose_pair.py <before dir> <after dir> <out.jpg> <prefix> \
        <before label> <after label> station [...]

``prefix`` is what look_shots put before a station's name ("" in the level's own light, "INSPECT_studio_" in the
inspection light). A missing frame FAILS rather than leaving a blank. Copied from
`docs/findings/teller_queue_275/compose_sheet.py`, its columns made a pair. Writes a JPG and stops.
"""
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFont

before, after, out, prefix, lb, la = sys.argv[1:7]
stations = sys.argv[7:]
W, H, PAD, HEAD = 800, 450, 6, 22
font = ImageFont.load_default()
sheet = Image.new("RGB", (2 * W + 3 * PAD, len(stations) * (H + HEAD + PAD) + PAD), (24, 24, 24))
draw = ImageDraw.Draw(sheet)
for i, st in enumerate(stations):
    for col, (d, label) in enumerate(((before, lb), (after, la))):
        p = pathlib.Path(d) / (prefix + st + ".png")
        if not p.is_file():
            raise SystemExit("FAIL: no frame %s" % p)
        x = PAD + col * (W + PAD)
        y = PAD + i * (H + HEAD + PAD)
        draw.text((x + 4, y + 4), "%s -- %s" % (label, st), fill=(235, 235, 235), font=font)
        sheet.paste(Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS), (x, y + HEAD))
sheet.save(out, quality=88)
print("wrote", out, sheet.size)
