"""The open floors nobody named (roadmap 255), drawn for the walker: for each spec in Deli Counter's
`open_floor_baseline.json`, the storey plan `floorplan.py` draws, with each baselined open edge that
`layout_lint.open_floors` finds overlaid in red and labelled by its two rooms. A drawer: it writes one SVG per
storey and an index, prints what it drew, and names every baselined pair it could not find rather than dropping it.

    python open_floor_plans.py <out dir>

Frame: the spec's own -- metres, origin at the footprint centre, +x east, +y north -- mapped by floorplan's `_Tx`,
north up. An edge is the line two rooms meet along: axis "Y" a vertical line at x = pos from y lo to hi, axis "X"
a horizontal one at y = pos from x lo to hi.
"""
import json
import os
import sys
from pathlib import Path

FACTORY = Path(__file__).resolve().parents[3]
DC = FACTORY / "deli_counter"
# The output path is resolved BEFORE the chdir below: resolved after it, a relative path landed inside Deli Counter's
# working tree (2026-10-19, moved out at once; that afternoon's cold run 9336 recorded no added file).
out = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(DC))
os.chdir(DC)
import floorplan  # noqa: E402
import layout_lint  # noqa: E402
import spec_loader  # noqa: E402

out.mkdir(parents=True, exist_ok=True)
base = json.loads((DC / "open_floor_baseline.json").read_text(encoding="utf-8"))
if not isinstance(base.get("open_floors"), dict):
    raise SystemExit("open_floor_baseline.json has no open_floors dict: not the shape this reads")
index, missing, drawn = [], [], 0
for name in sorted(base["open_floors"]):
    path = DC / "specs" / (name + ".json")
    raw = json.loads(path.read_text(encoding="utf-8"))
    spec = spec_loader.load_spec(str(path))
    want = set(base["open_floors"][name])
    found = layout_lint.open_floors(raw)
    rows = []
    for f in found:
        key = "%s|%s" % (f["a"], f["b"])
        if key in want or "%s|%s" % (f["b"], f["a"]) in want:
            rows.append(f)
    got = {"%s|%s" % (f["a"], f["b"]) for f in rows} | {"%s|%s" % (f["b"], f["a"]) for f in rows}
    for k in sorted(want):
        if k not in got:
            missing.append((name, k))
    tx = floorplan._Tx(spec)
    for story in sorted({f["story"] for f in rows}):
        svg = floorplan.render_story(spec, story)
        over = ['<g id="open_floors" font-size="13" font-weight="700">']
        for f in [r for r in rows if r["story"] == story]:
            if f["axis"] == "Y":
                x0 = x1 = tx.x(f["pos"])
                y0, y1 = tx.y(f["lo"]), tx.y(f["hi"])
            else:
                y0 = y1 = tx.y(f["pos"])
                x0, x1 = tx.x(f["lo"]), tx.x(f["hi"])
            over.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#e0242f" stroke-width="7" '
                        'stroke-linecap="round" opacity="0.85"/>' % (x0, y0, x1, y1))
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            label = "%s | %s  (%.1f m open)" % (f["a"], f["b"], f["uncovered"])
            over.append('<text x="%.1f" y="%.1f" fill="#e0242f" stroke="#ffffff" stroke-width="4" '
                        'paint-order="stroke" text-anchor="middle">%s</text>' % (mx, my - 8, floorplan._esc(label)))
            drawn += 1
        over.append("</g>")
        assert svg.rstrip().endswith("</svg>"), "floorplan's SVG does not end where this expects"
        svg = svg.rstrip()[:-len("</svg>")] + "\n".join(over) + "\n</svg>\n"
        fn = "%s_story%s.svg" % (name, story)
        (out / fn).write_text(svg, encoding="utf-8")
        index.append({"spec": name, "story": story, "file": fn,
                      "pairs": [{"a": f["a"], "b": f["b"], "uncovered_m": round(f["uncovered"], 2)}
                                for f in rows if f["story"] == story]})
(out / "index.json").write_text(json.dumps(index, indent=1), encoding="utf-8")
total = sum(len(v) for v in base["open_floors"].values())
print("baseline pairs %d in %d specs; drawn %d on %d storey plans; not found %d"
      % (total, len(base["open_floors"]), drawn, len(index), len(missing)))
for name, k in missing:
    print("  NOT FOUND today:", name, k)
