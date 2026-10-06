"""Where Lot's `place_enemies` puts a staged candidate's enemies, under three
keep-out rules. Measures; names no cause.

    python place_variants.py [--stage DIR] [--lot DIR] [--footprints]

- A, buildings only: what 0.97.2 asked.
- B, buildings and blockers: the Empties kept out, nothing else.
- C, buildings, blockers and the band behind each Empty row's front line:
  what 0.97.3 asks. On 0.97.3 code, C runs the shipped functions unpatched.

The flags:
- `--stage DIR`: a staged Laser Tag candidate. The default is cold run 9186's
  seed_9205. Its inputs are the site as Lot drew it (`site.site.drawn.json`)
  and the walk positions its scene was written from (`LT_PlayerRoutePoints`).
- `--lot DIR`: a Lot checkout or copy. The default is the factory's `lot`.
- Occluders are Lot's collision reading (`site_collision.read_site`), as
  `assemble` passes it. With it, 0.97.2 reproduces every shipped enemy
  exactly, on all six candidates checked in 9174 and 9186.
- `--footprints` uses the declared-footprint fallback instead, which
  `place_enemies` takes when the reading is incomplete.

Frame: level, x and y north, metres. A blocker's rect and the band are read
here with this script's own arithmetic, never through the code under test.

ON 0.97.2 ONLY `footprints` CAN BE PATCHED, and it answers two questions in
`place_enemies`: the keep-out (`rects`, default margin) and, through
`sight_occluders` on the fallback, the sightline occluders (`margin=0.0`).
The variants change the first and pass the second through, as 0.97.3 does.

REFUTED, KEPT.
- The first run of this comparison used the footprint fallback without
  saying so. It changed both questions at once, crediting the Empties and
  the band as cover.
- Its figures, that keeping the Empties out pushed Enemy_4 on through its
  house to the strip behind the row, are the FALLBACK's
  (`place_variants_0972_footprints.txt`).
- With the collision reading Lot actually passes, Enemy_4 never moves, and
  the band adds nothing on 9186's seed_9205 (`place_variants_0972.txt`).
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
LOT = (pathlib.Path(sys.argv[sys.argv.index("--lot") + 1]) if "--lot" in sys.argv
       else ROOT / "lot")
sys.path.insert(0, str(LOT))
import site_collision  # noqa: E402
import site_extent    # noqa: E402
import site_fences    # noqa: E402
import site_spawns    # noqa: E402
import site_streets   # noqa: E402

STAGE = (pathlib.Path(sys.argv[sys.argv.index("--stage") + 1]) if "--stage" in sys.argv
         else ROOT / "workspaces" / "cold-9186-ws" / ".level_factory" / "staging"
         / "restaurant_row_001.laser_tag_evaluate.candidate.seed_9205")
M = site_spawns.WALL_MARGIN
NODE = re.compile(r'\[node name="([^"]+)"[^\]]*\]\r?\ntransform = Transform3D\(([^)]*)\)')


def scene_points(stage):
    """``{node name: (x, y north, height)}`` for every transformed node in the
    staged scene, Godot (x, y, z) -> level (x, -z, y)."""
    lvl = (stage / "level.tscn").read_bytes().decode("utf-8")
    out = {}
    for m in NODE.finditer(lvl):
        v = [float(x) for x in m.group(2).split(",")]
        out[m.group(1)] = (v[9], -v[11], v[10])
    return out


def own_blocker(bk):
    x, y = float(bk["at"][0]), float(bk["at"][1])
    sx = float(bk.get("size_x", 12.0) or 12.0) / 2.0
    sy = float(bk.get("size_y", 12.0) or 12.0) / 2.0
    return (x - sx, y - sy, x + sx, y + sy)


def grow(r, by):
    return (r[0] - by, r[1] - by, r[2] + by, r[3] + by)


def own_bands(spec):
    ground = site_extent.resolve(spec).rect
    out = []
    for axis, members in site_fences.rows(spec):
        front, sign = site_fences.front_line(axis, members, site_streets.roads(spec), ground)
        lo_i = 1 if axis == 0 else 0
        band = list(ground)
        if sign > 0:
            band[lo_i + 2] = front
        else:
            band[lo_i] = front
        out.append(tuple(band))
    return out


def inside(p, r):
    return r[0] <= p[0] <= r[2] and r[1] <= p[1] <= r[3]


def clearance(p, r):
    """Distance from ``p`` to the rect, 0 inside it."""
    dx = max(r[0] - p[0], 0.0, p[0] - r[2])
    dy = max(r[1] - p[1], 0.0, p[1] - r[3])
    return (dx * dx + dy * dy) ** 0.5


def main():
    spec = json.loads((STAGE / "site.site.drawn.json").read_bytes().decode("utf-8"))
    pts = scene_points(STAGE)
    pos = {k: pts["Route_%d" % i] for i, k in enumerate(("spawn", "objective", "extraction"))}
    shipped_enemies = [pts["Enemy_%d" % i][:2] for i in range(6) if "Enemy_%d" % i in pts]
    blockers = {bk["id"]: own_blocker(bk) for bk in spec.get("blockers", [])}
    bands = own_bands(spec)
    solids = None if "--footprints" in sys.argv else site_collision.read_site(spec, [str(STAGE)])
    print("site:", STAGE.name)
    print(LOT.joinpath("VERSION").read_text().strip(), "at", LOT)
    print("occluders:", "declared footprints" if solids is None else
          "collision reading, complete: %s" % solids.complete)
    print("Empty rows: %d, bands %s" % (len(bands), [tuple(round(c, 2) for c in b) for b in bands]))
    shipped = hasattr(site_spawns, "solid_rects")
    orig_fp = site_spawns.footprints
    orig_solid = getattr(site_spawns, "solid_rects", None)
    orig_band = getattr(site_spawns, "shut_band_rects", None)

    def a_rects(s, margin=M):
        return orig_fp(s, margin)

    def b_rects(s, margin=M):
        return orig_fp(s, margin) + [grow(r, margin) for r in blockers.values()]

    def c_rects(s, margin=M):
        return b_rects(s, margin) + [grow(b, margin) for b in bands]

    def keep_out_only(variant):
        """0.97.2: change the keep-out, pass the occluder call through."""
        def fp(s, margin=M):
            return orig_fp(s, margin) if margin == 0.0 else variant(s, margin)
        return fp

    def no_band(s, margin=M):
        return []

    variants = [("A buildings only", a_rects, no_band),
                ("B and the blockers", b_rects, no_band),
                ("C and the band", None, None)]
    for label, solid, band in variants:
        if shipped:
            if solid is None:
                site_spawns.solid_rects, site_spawns.shut_band_rects = orig_solid, orig_band
                label += " (shipped code, unpatched)"
            else:
                site_spawns.solid_rects, site_spawns.shut_band_rects = solid, band
        else:
            site_spawns.footprints = keep_out_only(solid if solid is not None else c_rects)
        plan = site_spawns.place_enemies(spec, pos, solids=solids)
        site_spawns.footprints = orig_fp
        placed = [tuple(round(c, 2) for c in p[:2]) for p in plan.positions]
        same = placed == [tuple(round(c, 2) for c in p) for p in shipped_enemies]
        print("\n" + label + ("  == the shipped scene" if same else ""))
        for i, p in enumerate(plan.positions):
            hits = [bid for bid, r in blockers.items() if inside(p, r)]
            gap = min((clearance(p, b) for b in bands), default=None)
            where = ("no Empty row" if gap is None else
                     "BEHIND A FRONT LINE" if gap == 0.0 else
                     "%.2f m clear of the band" % gap)
            print("  Enemy_%d (%7.2f, %7.2f)  %-8s %s" % (i, p[0], p[1], ",".join(hits) or "open", where))
        print("  pushed", [(i, d) for i, d in plan.pushed], "dropped", plan.dropped)
    if shipped:
        site_spawns.solid_rects, site_spawns.shut_band_rects = orig_solid, orig_band


if __name__ == "__main__":
    main()
