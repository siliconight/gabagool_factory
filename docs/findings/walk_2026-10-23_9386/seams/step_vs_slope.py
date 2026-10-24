"""Finding 2: is a frame's brightness step at a wall position explained by WHERE THE POSITION IS (a module joint) or
by HOW STEEPLY THE BAKE'S LIGHT CHANGES THERE (the lightmap's slope)? The joints-against-mid-module comparison
(`joints_in_frame.py`) cannot tell these apart if the ceiling lamps' pools sit on the same 2 m grid as the modules.

    python step_vs_slope.py <lm_wall_profile out.txt> <frame.png> [<x0> <x1> <dx>]

For positions x0..x1 every dx (default -10.6 .. 4.6 every 0.1 m), the frame step exactly as `joints_in_frame.py`
measures it (the same camera, the same 3-5 px either side, rows 0.8-2.4 m), and the lightmap's slope there from the
profile (luminance per metre, the profile's samples 0.25 m either side). Each position is labelled `joint` (within
0.05 m of a module edge), `mid` (within 0.05 m of a module centre) or `-`. Excluded: the room's corner and the
bookshelf (x < -10.6, -7.3 < x < -6.3) and the door opening (0.3 < x < 1.7), as the README excludes them. Prints the
rows and, per label, the mean step and mean |slope|; then the steps of positions whose |slope| lies in the joints'
own |slope| range, by label. Measurements only.
"""
import math
import re
import sys

from PIL import Image  # noqa: E402

eye, tgt, W, H, fov = (-8.0, 1.6, -0.1), (-6.0, 2.07, -10.5), 1600, 900, math.radians(75)
WALL_Z = -6.34
JOINTS = [-10.85, -8.85, -6.85, -4.85, -2.85, -0.85, 0.3, 1.7, 3.7]
MIDS = [j + 1.0 for j in JOINTS]


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def norm(a):
    l = math.sqrt(sum(x * x for x in a))
    return tuple(x / l for x in a)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


f = norm(sub(tgt, eye))
r = norm(cross(f, (0, 1, 0)))
u = cross(r, f)
fy = (H / 2) / math.tan(fov / 2)


def proj(p):
    d = sub(p, eye)
    z = dot(d, f)
    return (W / 2 + dot(d, r) / z * fy, H / 2 - dot(d, u) / z * fy)


prof_path, frame_path = sys.argv[1], sys.argv[2]
x0, x1, dx = (float(a) for a in sys.argv[3:6]) if len(sys.argv) >= 6 else (-10.6, 4.6, 0.1)
prof = []
for line in open(prof_path, encoding="utf-8", errors="replace"):
    m = re.match(r"x\s+(-?[\d.]+) uv2 .* lum ([\d.]+)", line)
    if m:
        prof.append((float(m[1]), float(m[2])))
assert len(prof) > 20, "the profile holds %d samples: not a lm_wall_profile output" % len(prof)


def lum_at(x):
    best = min(prof, key=lambda p: abs(p[0] - x))
    assert abs(best[0] - x) < 0.051, "no profile sample within 5 cm of %.2f" % x
    return best[1]


im = Image.open(frame_path).convert("L")
assert im.size == (W, H), "%s is %s, not %dx%d" % (frame_path, im.size, W, H)


def col_mean(x, y0, y1):
    return sum(im.getpixel((x, y)) for y in range(y0, y1)) / (y1 - y0)


def frame_step(x):
    xs = [proj((x, h, WALL_Z)) for h in (0.8, 2.4)]
    cx = proj((x, 1.6, WALL_Z))[0]
    y0, y1 = int(min(p[1] for p in xs)), int(max(p[1] for p in xs))
    L = sum(col_mean(int(cx) - k, y0, y1) for k in (3, 4, 5)) / 3
    R = sum(col_mean(int(cx) + k, y0, y1) for k in (3, 4, 5)) / 3
    return cx, L - R


def label(x):
    if any(abs(x - j) <= 0.05 for j in JOINTS):
        return "joint"
    if any(abs(x - m) <= 0.05 for m in MIDS):
        return "mid"
    return "-"


rows = []
n = int(round((x1 - x0) / dx))
for i in range(n + 1):
    x = round(x0 + i * dx, 3)
    if x < -10.6 or -7.3 < x < -6.3 or 0.3 < x < 1.7:
        continue
    try:
        slope = (lum_at(x + 0.25) - lum_at(x - 0.25)) / 0.5
    except AssertionError:
        continue
    cx, s = frame_step(x)
    if not (8 < cx < W - 8):
        continue
    rows.append((x, label(x), cx, s, slope))
    print("x %6.2f %-5s column %6.1f  frame step (L-R) %6.2f  lightmap slope %7.4f /m" % (x, label(x), cx, s, slope))

print("== %s against %s" % (frame_path, prof_path))
for lab in ("joint", "mid", "-"):
    sel = [r_ for r_ in rows if r_[1] == lab]
    if sel:
        print("%-5s n %3d  mean |step| %.2f  mean |slope| %.4f" % (lab, len(sel), sum(abs(r_[3]) for r_ in sel) / len(sel),
                                                                   sum(abs(r_[4]) for r_ in sel) / len(sel)))
js = [abs(r_[4]) for r_ in rows if r_[1] == "joint"]
if js:
    lo, hi = min(js), max(js)
    print("positions whose |slope| is inside the joints' range %.4f..%.4f:" % (lo, hi))
    for lab in ("joint", "mid", "-"):
        sel = [r_ for r_ in rows if r_[1] == lab and lo <= abs(r_[4]) <= hi]
        if sel:
            print("  %-5s n %3d  mean |step| %.2f  mean |slope| %.4f" % (lab, len(sel), sum(abs(r_[3]) for r_ in sel) / len(sel),
                                                                       sum(abs(r_[4]) for r_ in sel) / len(sel)))
