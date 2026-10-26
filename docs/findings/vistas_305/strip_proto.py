"""A TEST horizon strip for roadmap 305's far band: procedural silhouettes, not the product. The product renders Zoo
species; this exists to price the sky-shader composite and to see a strip at the horizon at all.

    python strip_proto.py <out dir>

Writes horizon_day.png and horizon_night.png: RGBA, equirectangular in azimuth (u 0..1 is SKY_COORDS.x), 4096 x 128,
the rows spanning elevation BOTTOM_DEG (row 127) to TOP_DEG (row 0). Sectors by u: an airport (a low terminal, a
control tower with its cab, parked tails), a mall (one big box), a forest ridge, a city skyline. Day: hazy blue-grey
by distance; night: near-black with lit windows, a red beacon, runway and lot lights. Alpha 1 on a silhouette, 0
above it; the bottom rows fade so the band meets the fog.
"""
import math
import random
import sys

from PIL import Image

W, H = 4096, 128
BOTTOM_DEG, TOP_DEG = -1.0, 8.0
rng = random.Random(305)


def row_of(deg):
    return int(round((TOP_DEG - deg) / (TOP_DEG - BOTTOM_DEG) * (H - 1)))


def col_of(u):
    return int(u * W) % W


day = Image.new("RGBA", (W, H), (0, 0, 0, 0))
night = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dp, npx = day.load(), night.load()
HAZE = {"airport": (118, 128, 146), "mall": (112, 120, 136), "forest": (78, 92, 96), "city": (104, 112, 132)}
DARK = (8, 9, 13)


def column(x, top_deg, kind, lit=()):
    """Fill column x from the horizon band's bottom to top_deg; `lit` is a list of (deg, rgb) night lights."""
    top = row_of(top_deg)
    for y in range(max(0, top), H):
        fade = min(1.0, (H - 1 - y) / 10.0 + 0.15)
        a = int(255 * fade)
        r, g, b = HAZE[kind]
        shade = 1.0 - 0.06 * ((x // 7 + y // 9) % 2)
        dp[x, y] = (int(r * shade), int(g * shade), int(b * shade), a)
        npx[x, y] = DARK + (a,)
    for deg, rgb in lit:
        y = row_of(deg)
        if 0 <= y < H and y >= top:
            npx[x, y] = rgb + (255,)


# the airport, u 0.02..0.16: a terminal 0.9 deg, a tower 4.2 deg (a column fills from the ground, so no cab wider than its shaft), tails
for x in range(col_of(0.02), col_of(0.16)):
    u = x / W
    h = 0.9
    lit = [(0.5, (255, 214, 150))] if x % 5 == 0 else []
    if col_of(0.085) <= x < col_of(0.088):
        h = 4.2
        lit = [(4.0, (255, 40, 30))] if x == col_of(0.0865) else [(3.8, (170, 220, 255))]
    if (x // 40) % 3 == 0 and x % 40 < 6:
        h = max(h, 1.6)
    column(x, h, "airport", lit + [(0.1, (255, 180, 80))] if x % 11 == 0 else lit)
# the mall, u 0.24..0.32: one big box, its sign
for x in range(col_of(0.24), col_of(0.32)):
    lit = [(1.2, (255, 60, 90))] if col_of(0.27) <= x < col_of(0.285) else []
    if x % 9 == 0:
        lit.append((0.05, (255, 200, 120)))
    column(x, 1.5, "mall", lit)
# the forest ridge, u 0.40..0.72
for x in range(col_of(0.40), col_of(0.72)):
    u = x / W
    h = 1.6 + 1.1 * math.sin(u * 37.0) + 0.5 * math.sin(u * 151.0) + rng.uniform(-0.15, 0.15)
    column(x, max(0.3, h), "forest")
# the skyline, u 0.80..0.94
towers = []
x = col_of(0.80)
while x < col_of(0.94):
    w = rng.randint(14, 46)
    towers.append((x, w, rng.uniform(2.0, 7.5)))
    x += w + rng.randint(0, 10)
for x0, w, h in towers:
    for x in range(x0, min(x0 + w, W)):
        lit = [(d, (255, 222, 160)) for d in [0.4 + 0.45 * k for k in range(int(h / 0.45))]
               if rng.random() < 0.35 and (x - x0) % 4 != 0]
        if x == x0 + w // 2 and h > 6.0:
            lit.append((h - 0.1, (255, 40, 30)))
        column(x, h, "city", lit)

out = sys.argv[1]
day.save(out + "/horizon_day.png")
night.save(out + "/horizon_night.png")
print("wrote %s/horizon_day.png and horizon_night.png, %dx%d, elevation %.1f..%.1f deg" % (out, W, H, BOTTOM_DEG, TOP_DEG))
