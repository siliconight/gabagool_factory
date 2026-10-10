"""Roadmap 225: how large are the connected regions of changed pixels at a shot-bot station?

    python docs/findings/shotbot_sparkle/regions.py <shots dir> <station> [<station> ...]

On the grid the shot bot samples (every second pixel each way), marks a sample changed when some
channel differs by more than 12 of 255 between the station's two frames (`<station>.png` and
`<station>_b.png`, from `make_pair_probe.py`), and joins changed samples that touch on an edge.
Prints, per station: the changed share, the largest region, and the share of changed samples
that lie in regions of at least 4, 16, 64 and 256 samples. It measures and stops.
"""
import sys
from collections import deque
from pathlib import Path

from PIL import Image

DIFF_TOL = 12
SIZES = (4, 16, 64, 256)


def regions(a, b):
    w, h = a.size
    pa, pb = a.load(), b.load()
    gw, gh = w // 2, h // 2
    mask = [[False] * gw for _ in range(gh)]
    for gy in range(gh):
        for gx in range(gw):
            ca, cb = pa[gx * 2, gy * 2], pb[gx * 2, gy * 2]
            mask[gy][gx] = max(abs(ca[0] - cb[0]), abs(ca[1] - cb[1]),
                               abs(ca[2] - cb[2])) > DIFF_TOL
    seen = [[False] * gw for _ in range(gh)]
    sizes = []
    for gy in range(gh):
        for gx in range(gw):
            if not mask[gy][gx] or seen[gy][gx]:
                continue
            n, q = 0, deque([(gx, gy)])
            seen[gy][gx] = True
            while q:
                x, y = q.popleft()
                n += 1
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= nx < gw and 0 <= ny < gh and mask[ny][nx] and not seen[ny][nx]:
                        seen[ny][nx] = True
                        q.append((nx, ny))
            sizes.append(n)
    return sizes, gw * gh


def main(d, stations):
    d = Path(d)
    print("%-22s %8s %8s  %s" % ("station", "changed", "largest",
                                  "  ".join("in >=%d" % s for s in SIZES)))
    for st in stations:
        a = Image.open(d / f"{st}.png").convert("RGB")
        b = Image.open(d / f"{st}_b.png").convert("RGB")
        sizes, total = regions(a, b)
        changed = sum(sizes)
        shares = ["%6.1f%%" % (100.0 * sum(s for s in sizes if s >= k) / max(changed, 1))
                  for k in SIZES]
        print("%-22s %7.2f%% %8d  %s" % (st, 100.0 * changed / total, max(sizes, default=0),
                                         "  ".join(shares)))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
