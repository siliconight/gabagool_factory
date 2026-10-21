"""The share of each frame's pixels that moved by more than 15 of 255 between two runs' shots of the same stations,
in both lights (`docs/findings/denser_rooms_148/shots.sh`'s layout: <dir>/<label>_lit/<station>.png,
<label>_inspect/INSPECT_studio_<station>.png). Copied from that finding's `frame_change.py`, its labels made arguments.
Prints what it measured and stops.

    python frame_change.py <shots dir> <left label> <right label>
"""
import os
import sys

from PIL import Image, ImageChops

d, LEFT, RIGHT = sys.argv[1:4]
names = sorted(f[:-4] for f in os.listdir(os.path.join(d, LEFT + "_lit")) if f.endswith(".png"))
print("%-18s %8s %8s" % ("station", "lit", "inspect"))
for n in names:
    row = []
    for light, pre in (("lit", ""), ("inspect", "INSPECT_studio_")):
        a = Image.open(os.path.join(d, LEFT + "_" + light, pre + n + ".png")).convert("RGB")
        b = Image.open(os.path.join(d, RIGHT + "_" + light, pre + n + ".png")).convert("RGB")
        h = ImageChops.difference(a, b).convert("L").histogram()
        row.append(100.0 * sum(h[16:]) / sum(h))
    print("%-18s %7.1f%% %7.1f%%" % (n, row[0], row[1]))
