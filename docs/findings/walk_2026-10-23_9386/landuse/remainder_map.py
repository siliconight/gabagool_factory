"""Finding 7 ("this empty space goes against the doc..."): WHERE a site's remainder is -- ground no use claims -- as a
map and as pieces. The grid is the census's own: `tools/landuse_census.measure` runs as it does for the census row,
and the grid it hands `site_landuse._largest_blob` is kept.

    python remainder_map.py <site.json> <site.site.gameplay.json> <out.png> [--with-blockers]

Prints the uses' shares from that grid and the census's own shares beside them (they must be equal, or this is not
its grid -- a first draft that painted the spec alone found no buildings, the footprints coming from the gameplay),
then every remainder piece of at least MIN_PIECE_M2: its area, its centre (site plan metres), its bounding box, and
whether it touches the plate's edge (a verge or the fence's strip) or not (interior ground). Writes the map: one colour
a use, remainder in red, the pieces numbered, the gameplay's cover pieces as yellow dots. Measurements only.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "lot"))
sys.path.insert(0, str(ROOT / "tools"))
import landuse_census  # noqa: E402
import site_landuse as L  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

MIN_PIECE_M2 = 200.0
COLOURS = {"building": (70, 70, 80), "road": (40, 40, 40), "kerbcut": (60, 60, 60), "sidewalk": (150, 150, 150),
           "frontage": (120, 140, 160), "path": (170, 150, 110), "courtyard": (110, 160, 110), "yard": (90, 140, 90),
           "service": (160, 120, 80), "parking": (90, 90, 140), "remainder": (200, 60, 60)}

args = [a for a in sys.argv[1:] if not a.startswith("--")]
spec_p, gp_p, out = pathlib.Path(args[0]), pathlib.Path(args[1]), pathlib.Path(args[2])
captured = {}
_orig = L._largest_blob


def _keep(grid, use):
    captured["grid"] = grid
    return _orig(grid, use)


L._largest_blob = _keep
res = landuse_census.measure(spec_p, gp_p)
L._largest_blob = _orig
assert res.get("ok") and "grid" in captured, res
grid = captured["grid"]
rect = res["plate"]
ny, nx = len(grid), len(grid[0])
counts = {}
for row in grid:
    for v in row:
        counts[v] = counts.get(v, 0) + 1
total = nx * ny
mine = {u: round(counts.get(u, 0) / total, 4) for u in res["shares"]}
# THE EMPTIES AS BUILT LAND (`--with-blockers`): the census paints `buildings` only, and a street's Empties are the
# spec's `blockers` -- 26 of them on restaurant_row_001 -- so their footprints read as remainder. Painted here over
# the census's grid, after the shares check above, as `site_extent.rotated_footprint` gives each.
if "--with-blockers" in sys.argv:
    import site_extent
    spec_doc = json.loads(spec_p.read_text(encoding="utf-8"))
    nb = 0
    for bl in spec_doc.get("blockers", []) or []:
        # a blocker carries `size_x` / `size_y`, where `rotated_footprint` reads `footprint` (a first run of this
        # painted none of 26)
        r = site_extent.rotated_footprint(dict(bl, footprint=[bl["size_x"], bl["size_y"]]))
        if r is not None:
            # over REMAINDER cells: `_paint` fills only unassigned ones, and the census has assigned every cell by
            # now (a second run of this painted 26 blockers and moved no share)
            for j in range(len(grid)):
                y = rect[1] + (j + 0.5) * L.CELL
                if not (r[1] <= y <= r[3]):
                    continue
                for i in range(len(grid[0])):
                    x = rect[0] + (i + 0.5) * L.CELL
                    if r[0] <= x <= r[2] and grid[j][i] == "remainder":
                        grid[j][i] = "building"
            nb += 1
    counts = {}
    for row in grid:
        for v in row:
            counts[v] = counts.get(v, 0) + 1
    print("with %d blockers painted as building: " % nb + " ".join(
        "%s %.3f" % (u, counts.get(u, 0) / total) for u in res["shares"] if counts.get(u)))
print("plate %s, %d x %d cells of %.1f m" % (rect, nx, ny, L.CELL))
print("shares (this grid) " + " ".join("%s %.3f" % (u, v) for u, v in mine.items() if v))
print("shares (census)    " + " ".join("%s %.3f" % (u, v) for u, v in res["shares"].items() if v))
assert mine == res["shares"], "not the census's grid"

seen = [[False] * nx for _ in range(ny)]
pieces = []
for j in range(ny):
    for i in range(nx):
        if grid[j][i] != "remainder" or seen[j][i]:
            continue
        stack, cells = [(i, j)], []
        seen[j][i] = True
        while stack:
            a, b = stack.pop()
            cells.append((a, b))
            for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                c, e = a + da, b + db
                if 0 <= c < nx and 0 <= e < ny and not seen[e][c] and grid[e][c] == "remainder":
                    seen[e][c] = True
                    stack.append((c, e))
        pieces.append(cells)
pieces.sort(key=len, reverse=True)
x0, y0 = rect[0], rect[1]
big = [p for p in pieces if len(p) * L.CELL * L.CELL >= MIN_PIECE_M2]
print("remainder pieces %d, %d of at least %.0f m2 (the census's largest blob %.0f m2)" % (
    len(pieces), len(big), MIN_PIECE_M2, res["remainder_largest_blob"]))
for k, p in enumerate(big):
    xs = [a for a, _b in p]
    ys = [b for _a, b in p]
    edge = min(xs) == 0 or min(ys) == 0 or max(xs) == nx - 1 or max(ys) == ny - 1
    print("piece %2d  %7.0f m2  centre (%6.1f, %6.1f)  box x %6.1f..%6.1f y %6.1f..%6.1f  %s" % (
        k, len(p) * L.CELL * L.CELL, x0 + (sum(xs) / len(xs) + 0.5) * L.CELL, y0 + (sum(ys) / len(ys) + 0.5) * L.CELL,
        x0 + min(xs) * L.CELL, x0 + (max(xs) + 1) * L.CELL, y0 + min(ys) * L.CELL, y0 + (max(ys) + 1) * L.CELL,
        "touches the plate's edge" if edge else "interior"))

im = Image.new("RGB", (nx, ny))
px = im.load()
for j in range(ny):
    for i in range(nx):
        px[i, ny - 1 - j] = COLOURS.get(grid[j][i], (255, 0, 255))
im = im.resize((nx * 2, ny * 2), Image.NEAREST)
d = ImageDraw.Draw(im)
for k, p in enumerate(big):
    xs = [a for a, _b in p]
    ys = [b for _a, b in p]
    d.text((2 * sum(xs) / len(xs), 2 * (ny - 1 - sum(ys) / len(ys))), str(k), fill=(255, 255, 255))
gp = json.loads(gp_p.read_text(encoding="utf-8"))
n_cover = 0
for c in gp.get("cover", []) or []:
    pos = c.get("pos") or c.get("position") or ([c["x"], c["y"]] if "x" in c and "y" in c else None)
    if not pos:
        continue
    i, j = (pos[0] - x0) / L.CELL, (pos[1] - y0) / L.CELL
    d.ellipse((2 * i - 2, 2 * (ny - 1 - j) - 2, 2 * i + 2, 2 * (ny - 1 - j) + 2), fill=(255, 230, 0))
    n_cover += 1
im.save(out)
print("map %s, %d cover pieces drawn" % (out, n_cover))
