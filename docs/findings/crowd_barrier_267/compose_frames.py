"""Before and after, side by side: the same given stations photographed in two packages by `tools/look_shots.py`.

    python docs/findings/crowd_barrier_267/compose_frames.py <before dir> <after dir> <out.jpg> <prefix> <label a> <label b>
        [station ...]

Each row is one station, the before frame left and the after frame right, each scaled to 800 x 450 and labelled with
its column's label and the station's name. ``prefix`` is what look_shots put before a station's name ("" in the
level's own light, "INSPECT_studio_" in the inspection light). Writes a JPG and stops.
"""
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFont

a, b, out, prefix, la, lb = sys.argv[1:7]
stations = sys.argv[7:] or ["close_hook", "near", "normal", "far_line", "far_side"]
W, H, PAD, HEAD = 800, 450, 6, 22
font = ImageFont.load_default()
sheet = Image.new("RGB", (2 * W + 3 * PAD, len(stations) * (H + HEAD + PAD) + PAD), (24, 24, 24))
draw = ImageDraw.Draw(sheet)
for r, st in enumerate(stations):
    y = PAD + r * (H + HEAD + PAD)
    for c, (d, label) in enumerate(((a, la), (b, lb))):
        p = pathlib.Path(d) / (prefix + st + ".png")
        if not p.is_file():
            raise SystemExit("FAIL: no frame %s" % p)
        im = Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS)
        x = PAD + c * (W + PAD)
        draw.text((x + 4, y + 4), "%s -- %s" % (label, st), fill=(235, 235, 235), font=font)
        sheet.paste(im, (x, y + HEAD))
sheet.save(out, quality=88)
print("wrote", out, sheet.size)
