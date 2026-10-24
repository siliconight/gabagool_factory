"""Brightness step across each 2 m wall-module joint of pharmacy_a01's back-room north wall, against the same step at
mid-module positions (the control), in one frame shot from the walker's eye.

    python joints_in_frame.py <frame.png> [<frame.png> ...]

The camera is the walker's (`tools/look_shots.py --station seams:-8.0,1.6,-0.1,-6.0,2.07,-10.5`, 1600 x 900, fov 75).
Frame: Godot world, metres; the wall's face is z = -6.34; joints are the module edges `wall_islands.out.txt` read off
9389's merged mesh (x -10.85 .. 3.70, with the door opening's edges at 0.30 and 1.70). The step is |mean(left) -
mean(right)| in grey codes (0-255), each side the mean of the columns 3-5 px off the projected line, over the rows
the wall spans between 0.8 and 2.4 m. Prints what it measured; the reading is the README's.

First run inline on 2026-10-24 (output `joints_in_frame.out.txt`, the shipped frame only); saved here unchanged but
for taking its frames as arguments.
"""
import math
import sys

from PIL import Image

eye = (-8.0, 1.6, -0.1)
tgt = (-6.0, 2.07, -10.5)
W, H = 1600, 900
fov = math.radians(75)
WALL_Z = -6.34
JOINTS = [-10.85, -8.85, -6.85, -4.85, -2.85, -0.85, 0.3, 1.7, 3.7]
MIDS = [-9.85, -7.85, -5.85, -3.85, -1.85, 2.7, 4.7]


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


def measure(path):
    im = Image.open(path).convert("L")
    assert im.size == (W, H), "%s is %s, not the %dx%d this camera is" % (path, im.size, W, H)

    def col_mean(x, y0, y1):
        return sum(im.getpixel((x, y)) for y in range(y0, y1)) / (y1 - y0)

    def step(x, hs):
        xs = [proj((x, h, WALL_Z)) for h in hs]
        cx = proj((x, 1.6, WALL_Z))[0]
        if not (8 < cx < W - 8):
            return cx, None, None, None
        y0, y1 = int(min(p[1] for p in xs)), int(max(p[1] for p in xs))
        L = sum(col_mean(int(cx) - k, y0, y1) for k in (3, 4, 5)) / 3
        R = sum(col_mean(int(cx) + k, y0, y1) for k in (3, 4, 5)) / 3
        return cx, L, R, abs(L - R)

    print("==", path)
    rows, ctrl = [], []
    for jx in JOINTS:
        cx, L, R, s = step(jx, (0.8, 1.6, 2.4))
        if s is None:
            print("joint x=%.2f off frame (col %.0f)" % (jx, cx))
            continue
        rows.append(s)
        print("joint x=%6.2f -> column %4.0f  left %5.1f right %5.1f  step %4.1f" % (jx, cx, L, R, s))
    for mx in MIDS:
        cx, L, R, s = step(mx, (0.8, 2.4))
        if s is None:
            continue
        ctrl.append(s)
        print("mid-module x=%6.2f -> column %4.0f  step %4.1f" % (mx, cx, s))
    print("mean step at joints %.2f (n %d); at mid-module %.2f (n %d)"
          % (sum(rows) / len(rows), len(rows), sum(ctrl) / len(ctrl), len(ctrl)))


for p in sys.argv[1:]:
    measure(p)
