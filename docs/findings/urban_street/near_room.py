"""How much near-side frontage an urban site leaves between its obstacles, as `empties.infill` sees it (roadmap 241).

    python docs/findings/urban_street/near_room.py <site.json> [<deli_counter build dir>]

Reads a candidate's site spec as Level Factory wrote it (the `lot_assemble` job's input, under the workspace's
`temp/<mission>/candidate_<seed>/site.json`) and rebuilds what the compose stage handed `infill`: each mission
building's rect from its `at`, `rot` and the footprint `site_variation.shell_footprint` measures off its shell in
the build dir, every road's band (`empties._road_band`), and the near building line. Prints the line, each
obstacle along it (a building with its `NEAR_PASSAGE`, a road running north across the frontage), each room
between them in metres, and the narrowest mid-rise the library holds -- so a room under it is a room nothing
fits. Prints what it measured and stops.
"""
import json
import pathlib
import sys

F = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(F / "level_factory"))
from packages.pipeline import empties, site_variation, street_line   # noqa: E402

SPEC = pathlib.Path(sys.argv[1])
BUILD = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else F / "deli_counter" / "build"


def main():
    d = json.loads(SPEC.read_text(encoding="utf-8"))
    roads = d["roads"]
    _edge, line = empties._near_side(roads[0])
    mids = sorted(BUILD.glob("gs_midrise_*.glb"))
    widths = {}
    for g in mids:
        x0, x1, y0, y1 = street_line.shell_extents(str(g))
        widths[g.stem] = (round(x1 - x0, 2), round(y1 - y0, 2))
    deepest = max(w[1] for w in widths.values())
    print(f"near line y {line:.3f}; mid-rises (width, depth): {widths}")
    stops = []
    for b in d["buildings"]:
        aid = b.get("archetype") or pathlib.Path(b.get("glb") or b.get("scene") or "").stem
        if aid in ("site", "shell"):
            aid = pathlib.Path(b.get("scene") or b.get("glb")).parent.name
        glb = BUILD / f"{aid}.glb"
        fp = site_variation.shell_footprint(str(glb)) if glb.exists() else None
        r = empties.building_rect(b["at"], b["rot"], fp) if fp else None
        print(f"building {b['id']} {aid}: footprint {fp}, rect {tuple(round(v, 2) for v in r) if r else None}")
        if r and r[3] > line and r[2] < line + deepest:
            stops.append((r[0] - empties.NEAR_PASSAGE, r[1] + empties.NEAR_PASSAGE, f"{b['id']} + passage"))
    for i, rd in enumerate(roads[1:], 1):
        band = empties._road_band(rd)
        if band and band[3] > line and band[2] < line + deepest and (band[1] - band[0]) < (band[3] - band[2]):
            stops.append((band[0], band[1], f"road {i} (north-south)"))
        elif band:
            print(f"road {i} band y {band[2]:.2f}..{band[3]:.2f}: "
                  f"{'cuts' if band[2] < line + deepest and band[3] > line else 'clear of'} the {deepest} m band")
    stops.sort()
    x, x_end = -d["ground"]["size_x"] / 2.0 + empties.CLEARANCE, d["ground"]["size_x"] / 2.0 - empties.CLEARANCE
    for s in stops:
        print(f"  room {max(0.0, s[0] - x):6.2f} m  ({x:.2f} .. {s[0]:.2f}), then {s[2]} to {s[1]:.2f}")
        x = max(x, s[1])
    print(f"  room {max(0.0, x_end - x):6.2f} m  ({x:.2f} .. {x_end:.2f}), the plate's end")
    print(f"narrowest mid-rise: {min(w[0] for w in widths.values())} m")


if __name__ == "__main__":
    main()
