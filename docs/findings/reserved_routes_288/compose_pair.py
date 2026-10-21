"""Two runs' frames of the same rooms side by side, one row a room, the earlier run on the left: a JPEG with each
frame labelled. Prints what it wrote.

    python compose_pair.py <shots dir> <lit|inspect> <out.jpg> <left label> <right label> <room> [<room> ...]

<shots dir> holds `<label>_<light>/` folders as `docs/findings/denser_rooms_148/shots.sh` writes them (an inspection
frame is named `INSPECT_studio_<room>.png`); a label reads `r9369` and is captioned as the cold run it names.
"""
import os
import sys

from PIL import Image, ImageDraw

shots, light, out, left, right = sys.argv[1:6]
rooms = sys.argv[6:]
W, H = 800, 450
pre = "INSPECT_studio_" if light == "inspect" else ""
sheet = Image.new("RGB", (2 * W + 12, len(rooms) * (H + 28) + 4), "white")
g = ImageDraw.Draw(sheet)
for i, room in enumerate(rooms):
    y = i * (H + 28) + 4
    for j, label in enumerate((left, right)):
        im = Image.open(os.path.join(shots, "%s_%s" % (label, light), pre + room + ".png")).convert("RGB")
        x = j * (W + 12)
        sheet.paste(im.resize((W, H), Image.LANCZOS), (x, y + 24))
        g.text((x + 4, y + 6), "%s -- cold run %s (%s light)" % (room, label.lstrip("r"),
               "inspection" if light == "inspect" else "the level's own"), fill=(0, 0, 0))
sheet.save(out, quality=88)
print("wrote", out, sheet.size, "rooms:", ", ".join(rooms))
