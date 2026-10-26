"""Roadmap 306, step 1: what each piece of a site's remainder could BE -- a proposal drawn on a map, measurement only,
nothing placed. The grid is the census's (`tools/landuse_census.measure`, Lot >= 0.130.0, Empties counted).

    python classify_remainder.py <site.json> <site.site.gameplay.json> <out.png>

Each remainder cell takes the FIRST role whose test holds, in this order (site plan metres):
  fight     within FIGHT_M of the mission's legs (crew spawn -> each objective building's centre -> extraction), of an
            enemy or crew marker, or of a cover piece: ground the encounter may use, to keep open AS a named use
            (the land-use guide's 12: a vacant lot, a parking area, a forecourt, a work yard);
  rear      behind a building or an Empty -- past the face away from the road it fronts, inside its width, within
            REAR_M: rear yards and an alley (the guide's 6, a rowhouse block's and a main street's);
  frontage  within FRONT_M of a road's outer edge where no building or Empty fronts it: a facing row (the guide's 5.3);
  verge     within VERGE_M of the plate's edge: grass and walk to the fence;
  open      the rest: needs a reason, or a use.
A building's front is the side facing the nearest road centre line. Prints the area of each role and the map's legend;
the map draws the census's uses dimmed and the remainder in the role's colour. Measurements only.
"""
import json
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "lot"))
sys.path.insert(0, str(ROOT / "tools"))
import landuse_census  # noqa: E402
import site_landuse as L  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

FIGHT_M, REAR_M, FRONT_M, VERGE_M = 12.0, 25.0, 15.0, 8.0
ROLES = {"fight": (230, 90, 40), "rear": (90, 170, 90), "frontage": (80, 120, 220), "verge": (200, 200, 120),
         "open": (220, 40, 40)}

spec_p, gp_p, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3])
captured = {}
_orig = L._largest_blob
L._largest_blob = lambda grid, use: (captured.__setitem__("grid", grid), _orig(grid, use))[1]
res = landuse_census.measure(spec_p, gp_p)
L._largest_blob = _orig
assert res.get("ok") and "grid" in captured, res
grid = captured["grid"]
rect = res["plate"]
ny, nx = len(grid), len(grid[0])
spec = json.loads(spec_p.read_text(encoding="utf-8"))
gp = json.loads(gp_p.read_text(encoding="utf-8"))
roads = spec.get("roads", []) or []


def seg_dist(p, a, b):
    ax, ay, bx, by = a[0], a[1], b[0], b[1]
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / L2))
    return math.hypot(p[0] - (ax + t * dx), p[1] - (ay + t * dy))


# the solids that front roads: buildings (gameplay footprints) and Empties
solids = []
for b in gp.get("buildings", []) or []:
    fx, fy = b["footprint"]
    if (float(b.get("rot", 0)) % 180) == 90:
        fx, fy = fy, fx
    solids.append((b["id"], b["at"][0], b["at"][1], fx, fy))
for bl in spec.get("blockers", []) or []:
    fx, fy = bl["size_x"], bl["size_y"]
    if (float(bl.get("rot", 0)) % 180) == 90:
        fx, fy = fy, fx
    solids.append((bl["id"], bl["at"][0], bl["at"][1], fx, fy))


def front_of(cx, cy):
    """The unit vector from a solid toward its nearest road centre line, axis-snapped."""
    best = min(roads, key=lambda r: seg_dist((cx, cy), r["a"], r["b"]))
    a, b = best["a"], best["b"]
    if abs(a[1] - b[1]) < abs(a[0] - b[0]):          # an east-west road
        return (0.0, 1.0 if a[1] > cy else -1.0)
    return (1.0 if a[0] > cx else -1.0, 0.0)


fronts = [(sid, cx, cy, hx, hy, front_of(cx, cy)) for sid, cx, cy, hx, hy in solids]

# the mission's legs
pts = {}
for m in gp.get("site_markers", []) or []:
    if m.get("type") in ("crew_spawn", "extraction"):
        pts[m["type"]] = m["at"]
legs = []
obj_ids = [o for o in (spec.get("objective"),) if o]
centres = {sid: (cx, cy) for sid, cx, cy, _a, _b in solids}
if "crew_spawn" in pts:
    path = [pts["crew_spawn"]] + [centres[o] for o in obj_ids if o in centres] + ([pts["extraction"]] if "extraction" in pts else [])
    legs = list(zip(path, path[1:]))
points = [tuple(c[k] for k in ("x", "y")) for c in (gp.get("cover_plan") or {}).get("placed", []) or []]
#: the encounter's own points (the gameplay's `markers`, each `x`/`y`); a first draft read `at`/`pos` and an
#: enemy/guard type, matched none of 29 and called 94 m2 fight space
FIGHT_TYPES = ("attacker_spawn", "defender_spawn", "cover_low", "cover_high", "objective", "patrol_point", "extraction")
for m in gp.get("markers", []) or []:
    if m.get("type") in FIGHT_TYPES and "x" in m and "y" in m:
        points.append((float(m["x"]), float(m["y"])))
print("legs %d, cover and markers %d, solids %d (buildings %d, Empties %d)" % (
    len(legs), len(points), len(solids), len(gp.get("buildings", []) or []), len(spec.get("blockers", []) or [])))

# road outer edges, for frontage: each road's line offset by half its width plus its sidewalk
def fronted(p, r):
    """Whether a solid fronts road r near point p's projection on it."""
    a, b = r["a"], r["b"]
    ew = abs(a[1] - b[1]) < abs(a[0] - b[0])
    for _sid, cx, cy, hx, hy, (fx, fy) in fronts:
        if ew and fx == 0.0 and abs(p[0] - cx) <= hx / 2 + 1.0 and (cy < a[1]) == (p[1] < a[1]):
            return True
        if not ew and fy == 0.0 and abs(p[1] - cy) <= hy / 2 + 1.0 and (cx < a[0]) == (p[0] < a[0]):
            return True
    return False


area = {k: 0 for k in ROLES}
role_grid = [[None] * nx for _ in range(ny)]
x0, y0, x1, y1 = rect
for j in range(ny):
    y = y0 + (j + 0.5) * L.CELL
    for i in range(nx):
        if grid[j][i] != "remainder":
            continue
        x = x0 + (i + 0.5) * L.CELL
        p = (x, y)
        role = None
        if any(seg_dist(p, a, b) <= FIGHT_M for a, b in legs) or any(math.hypot(x - q[0], y - q[1]) <= FIGHT_M for q in points):
            role = "fight"
        if role is None:
            for _sid, cx, cy, hx, hy, (fx, fy) in fronts:
                # behind: past the back face (the face away from the front), within REAR_M, inside the width
                if fx == 0.0:
                    behind = (cy - fy * hy / 2.0 - y) * fy
                    inside = abs(x - cx) <= hx / 2.0
                else:
                    behind = (cx - fx * hx / 2.0 - x) * fx
                    inside = abs(y - cy) <= hy / 2.0
                if inside and 0.0 <= behind <= REAR_M:
                    role = "rear"
                    break
        if role is None:
            for r in roads:
                edge = r.get("width", 10.0) / 2 + r.get("sidewalk", 0.0)
                d = seg_dist(p, r["a"], r["b"])
                if edge <= d <= edge + FRONT_M and not fronted(p, r):
                    role = "frontage"
                    break
        if role is None and min(x - x0, x1 - x, y - y0, y1 - y) <= VERGE_M:
            role = "verge"
        role = role or "open"
        role_grid[j][i] = role
        area[role] += 1
cell_a = L.CELL * L.CELL
tot = sum(area.values())
print("remainder %.0f m2: " % (tot * cell_a) + "  ".join("%s %.0f m2 (%.0f %%)" % (k, v * cell_a, 100.0 * v / max(1, tot))
                                                           for k, v in area.items()))
im = Image.new("RGB", (nx, ny))
px = im.load()
for j in range(ny):
    for i in range(nx):
        r = role_grid[j][i]
        if r:
            px[i, ny - 1 - j] = ROLES[r]
        else:
            c = {"building": (70, 70, 80), "road": (40, 40, 40)}.get(grid[j][i], (120, 120, 120))
            px[i, ny - 1 - j] = c
im = im.resize((nx * 2, ny * 2), Image.NEAREST)
d = ImageDraw.Draw(im)
for k, (name, col) in enumerate(ROLES.items()):
    d.rectangle((6, 6 + 14 * k, 16, 16 + 14 * k), fill=col)
    d.text((20, 5 + 14 * k), name, fill=(255, 255, 255))
im.save(out)
print("map %s" % out)
