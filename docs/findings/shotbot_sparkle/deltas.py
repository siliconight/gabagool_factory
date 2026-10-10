"""Roadmap 225: how far does each changed pixel move, at a station's two frames?

    python docs/findings/shotbot_sparkle/deltas.py <shots dir> <station> [...]

On the shot bot's sampled grid (every second pixel each way), takes every sample whose largest
channel difference between `<station>.png` and `<station>_b.png` exceeds 12 of 255 (the shot
bot's DIFF_TOL), and prints how those differences are distributed: the share above 32, 64, 128 and
192, and the median. A pixel that z-fights swaps between two surfaces' colours; one that sparkles
shifts by a sub-pixel blend of one texture. It measures and stops.
"""
import sys
from pathlib import Path

from PIL import Image

DIFF_TOL = 12
EDGES = (32, 64, 128, 192)


def main(d, stations):
    d = Path(d)
    print("%-22s %8s %7s  %s" % ("station", "changed", "median",
                                 "  ".join(">%d" % e for e in EDGES)))
    for st in stations:
        a = Image.open(d / f"{st}.png").convert("RGB").load()
        b_img = Image.open(d / f"{st}_b.png").convert("RGB")
        b = b_img.load()
        w, h = b_img.size
        ds = []
        for y in range(0, h, 2):
            for x in range(0, w, 2):
                ca, cb = a[x, y], b[x, y]
                dd = max(abs(ca[0] - cb[0]), abs(ca[1] - cb[1]), abs(ca[2] - cb[2]))
                if dd > DIFF_TOL:
                    ds.append(dd)
        ds.sort()
        n = len(ds)
        med = ds[n // 2] if n else 0
        shares = "  ".join("%5.1f%%" % (100.0 * sum(1 for v in ds if v > e) / max(n, 1))
                           for e in EDGES)
        print("%-22s %8d %7d  %s" % (st, n, med, shares))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
