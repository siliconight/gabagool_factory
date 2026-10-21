"""Several packages' look shots side by side, one row a station, one column a package, each frame scaled to 640 x 360 and
labelled with its column's label and the station's name. Copied from
`docs/findings/cargo_container_267/compose_pair.py`, its two columns made any number.

    python docs/findings/car_wear_44/compose_columns.py <out.jpg> <prefix> <label>=<frames dir> [...] -- station [...]

``prefix`` is what look_shots put before a station's name ("" in the level's own light, "INSPECT_studio_" in the
inspection light). A missing frame FAILS rather than leaving a blank. Writes a JPG and stops.
"""
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFont

args = sys.argv[1:]
out, prefix = args[0], args[1]
cut = args.index("--")
cols = [a.split("=", 1) for a in args[2:cut]]
stations = args[cut + 1:]
W, H, PAD, HEAD = 640, 360, 6, 20
font = ImageFont.load_default()
sheet = Image.new("RGB", (len(cols) * (W + PAD) + PAD, len(stations) * (H + HEAD + PAD) + PAD), (24, 24, 24))
draw = ImageDraw.Draw(sheet)
for i, st in enumerate(stations):
    for j, (label, d) in enumerate(cols):
        p = pathlib.Path(d) / (prefix + st + ".png")
        if not p.is_file():
            raise SystemExit("FAIL: no frame %s" % p)
        x = PAD + j * (W + PAD)
        y = PAD + i * (H + HEAD + PAD)
        draw.text((x + 4, y + 4), "%s -- %s" % (label, st), fill=(235, 235, 235), font=font)
        sheet.paste(Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS), (x, y + HEAD))
sheet.save(out, quality=88)
print("wrote", out, sheet.size)
