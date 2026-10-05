"""Diff two folders of frames, view by view.

    python frame_diff.py <dir A> <dir B> [<heatmap out dir>]

For every PNG present in both: mean absolute difference over all channels
(0-255), the share of pixels with any channel off by more than 16, and the
share off by more than 48. Writes an amplified difference image per view when
an out dir is given. Prints what it measured and stops; a view in only one
folder is named, and no common view at all FAILS.
"""
import pathlib
import sys

from PIL import Image, ImageChops

a_dir, b_dir = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
out = pathlib.Path(sys.argv[3]) if len(sys.argv) > 3 else None
names = sorted({p.name for p in a_dir.glob("*.png")} & {p.name for p in b_dir.glob("*.png")})
only = sorted({p.name for p in a_dir.glob("*.png")} ^ {p.name for p in b_dir.glob("*.png")})
if not names:
    raise SystemExit("no view in both folders")
if out:
    out.mkdir(parents=True, exist_ok=True)
print(f"{'view':40s} {'mean |d|':>9s} {'>16':>8s} {'>48':>8s}")
for n in names:
    a = Image.open(a_dir / n).convert("RGB")
    b = Image.open(b_dir / n).convert("RGB")
    if a.size != b.size:
        print(f"{n:40s} sizes differ {a.size} vs {b.size}")
        continue
    d = ImageChops.difference(a, b)
    px = list(d.getdata())
    tot = len(px)
    mean = sum(sum(p) for p in px) / (3.0 * tot)
    over16 = sum(1 for p in px if max(p) > 16) / tot
    over48 = sum(1 for p in px if max(p) > 48) / tot
    print(f"{n:40s} {mean:9.3f} {100 * over16:7.2f}% {100 * over48:7.2f}%")
    if out:
        d.point(lambda v: min(255, v * 4)).save(out / n)
for n in only:
    print(f"{n:40s} only in one folder")
