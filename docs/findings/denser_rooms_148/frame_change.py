"""The share of each frame's pixels that moved by more than 15 of 255 between two runs' shots of the same stations,
in both lights (`shots.sh`'s layout: <dir>/r9368_lit/<station>.png, r9368_inspect/INSPECT_studio_<station>.png).
Prints what it measured and stops.

    python frame_change.py <shots dir>
"""
import os
import sys

from PIL import Image, ImageChops

d = sys.argv[1]
names = sorted(f[:-4] for f in os.listdir(os.path.join(d, "r9368_lit")) if f.endswith(".png"))
print("%-18s %8s %8s" % ("station", "lit", "inspect"))
for n in names:
    row = []
    for light, pre in (("lit", ""), ("inspect", "INSPECT_studio_")):
        a = Image.open(os.path.join(d, "r9368_" + light, pre + n + ".png")).convert("RGB")
        b = Image.open(os.path.join(d, "r9369_" + light, pre + n + ".png")).convert("RGB")
        h = ImageChops.difference(a, b).convert("L").histogram()
        row.append(100.0 * sum(h[16:]) / sum(h))
    print("%-18s %7.1f%% %7.1f%%" % (n, row[0], row[1]))
