"""Put two runs' frames of the same rooms side by side, one row a room, the control on the left: a JPEG with each frame
labelled by run and room. Prints what it wrote.

    python compose_rooms.py <shots dir> <light: lit|inspect> <out.jpg> <room> [<room> ...]

<shots dir> holds `r9368_<light>/` and `r9369_<light>/` as `shots.sh` writes them (an inspection frame is named
`INSPECT_studio_<room>.png`).
"""
import os
import sys

from PIL import Image, ImageDraw

shots, light, out = sys.argv[1:4]
rooms = sys.argv[4:]
W, H = 800, 450
LEFT, RIGHT = ("r9368", "cold run 9368, Deli Counter 0.245.0 (the control)"), ("r9369", "cold run 9369, Deli Counter 0.247.0")
pre = "INSPECT_studio_" if light == "inspect" else ""
sheet = Image.new("RGB", (2 * W + 12, len(rooms) * (H + 28) + 4), "white")
g = ImageDraw.Draw(sheet)
for i, room in enumerate(rooms):
    y = i * (H + 28) + 4
    for j, (run, label) in enumerate((LEFT, RIGHT)):
        p = os.path.join(shots, "%s_%s" % (run, light), pre + room + ".png")
        im = Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS)
        x = j * (W + 12)
        sheet.paste(im, (x, y + 24))
        g.text((x + 4, y + 6), "%s -- %s (%s light)" % (room, label, "inspection" if light == "inspect" else "the level's own"),
               fill=(0, 0, 0))
sheet.save(out, quality=88)
print("wrote", out, sheet.size, "rooms:", ", ".join(rooms))
