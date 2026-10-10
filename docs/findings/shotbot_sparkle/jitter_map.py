"""Where a shot-bot station's two frames differ: a map of the changed pixels, and where they are.

    python jitter_map.py <shots dir> <station> <out.png>

Changed means some channel differs by more than 12 of 255, the shot bot's DIFF_TOL. The map is
the first frame dimmed, with every changed pixel painted red. Prints the count, and the share of
changed pixels in each fifth of the frame's height, top to bottom.
"""
import sys
from pathlib import Path

from PIL import Image

DIFF_TOL = 12
d, st, out = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
a = Image.open(d / f"{st}.png").convert("RGB")
b = Image.open(d / f"{st}_b.png").convert("RGB")
w, h = a.size
pa, pb = a.load(), b.load()
m = a.point(lambda v: v // 3)
pm = m.load()
changed = 0
rows = [0] * 5
for y in range(h):
    for x in range(w):
        ca, cb = pa[x, y], pb[x, y]
        if max(abs(ca[0] - cb[0]), abs(ca[1] - cb[1]), abs(ca[2] - cb[2])) > DIFF_TOL:
            changed += 1
            rows[min(4, y * 5 // h)] += 1
            pm[x, y] = (255, 0, 0)
m.save(out)
print(f"{st}: {changed} of {w * h} pixels changed ({100.0 * changed / (w * h):.2f}%)")
print("  by fifth of the height, top first:", ", ".join(f"{100.0 * r / max(changed, 1):.0f}%" for r in rows))
