"""How far apart are two frames of one station?

    python frame_diff.py <a.png> <b.png>

Prints the mean absolute difference per channel over the whole frame (0..255 codes), the share of
pixels whose largest channel difference exceeds 8 codes and 32 codes, and the bounding box of the
pixels over 32. Two frames of one camera on one scene differ only where something moved -- a
failing tube's flicker, rain -- so the box says WHERE they differ, which the reader compares with
the frames. It prints what it measured and stops.
"""
import sys

from PIL import Image, ImageChops

a = Image.open(sys.argv[1]).convert("RGB")
b = Image.open(sys.argv[2]).convert("RGB")
if a.size != b.size:
    raise SystemExit("sizes differ: %s vs %s" % (a.size, b.size))
d = ImageChops.difference(a, b)
w, h = d.size
px = d.load()
total = [0, 0, 0]
over8 = over32 = 0
box = [w, h, -1, -1]
for y in range(h):
    for x in range(w):
        r, g, bl = px[x, y]
        total[0] += r
        total[1] += g
        total[2] += bl
        m = max(r, g, bl)
        if m > 8:
            over8 += 1
        if m > 32:
            over32 += 1
            box = [min(box[0], x), min(box[1], y), max(box[2], x), max(box[3], y)]
n = float(w * h)
print("[diff] %s vs %s: mean |d| (%.2f, %.2f, %.2f); >8 codes %.3f %%, >32 codes %.3f %%, box over 32 %s"
      % (sys.argv[1].replace("\\", "/").split("/")[-1], sys.argv[2].replace("\\", "/").split("/")[-2],
         total[0] / n, total[1] / n, total[2] / n, 100 * over8 / n, 100 * over32 / n,
         box if box[2] >= 0 else "none"))
