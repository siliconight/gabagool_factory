"""Draw what the open-floor table changed, before and after, on Deli Counter's own storey plans (roadmap 260).

    python plans.py <out dir> [--before COMMIT]      # default before: 9be68b3b (Deli Counter 0.233.0)

For each case below: the storey plan `floorplan.render_story` draws from the spec at COMMIT, and from the spec in the
working tree, the after plan overlaid with what moved -- wall that was not there in red, a door that was not there in
green, an opening that moved in orange, a pair the table named one floor as a dashed blue edge. Writes one HTML page
(`plans.html`) holding them side by side, and prints what it drew. Changes nothing in Deli Counter; the output path is
resolved before the chdir into it.

Frame: the spec's own -- metres, origin at the footprint centre, +x east, +y north -- mapped by floorplan's `_Tx`, north
up.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

FACTORY = Path(__file__).resolve().parents[3]
DC = FACTORY / "deli_counter"
out = Path(sys.argv[1]).resolve()
BEFORE = sys.argv[sys.argv.index("--before") + 1] if "--before" in sys.argv else "9be68b3b"
sys.path.insert(0, str(DC))
os.chdir(DC)
import floorplan  # noqa: E402
import layout_lint  # noqa: E402
import open_floor_rules  # noqa: E402
import spec_loader  # noqa: E402

CASES = [
    ("deli_a01", 0, "a deli's ground floor: the kitchen walled from the aisles, a door, the stockroom gate slid"),
    ("corner_deli_heist_01", -1, "corner_deli_heist_01's basement: the cold rooms walled apart; the stair well open"),
    ("rowhouse_raid", 0, "the rowhouse's ground floor: the garage bay closed, a kitchen-to-garage door, hall and kitchen open"),
    ("auto_shop_a01", 1, "an auto shop's upper floor: the office wall run on to the exterior wall both ends"),
]


def before_spec(name):
    text = subprocess.run(["git", "-C", str(DC), "show", "%s:specs/%s.json" % (BEFORE, name)],
                          capture_output=True, text=True, encoding="utf-8", check=True).stdout
    return json.loads(text)


def covered(spec, story, axis, pos):
    out_ = []
    for p in spec.get("partitions") or []:
        if int(p.get("story", 0) or 0) == story and p["axis"] == axis and abs(float(p["pos"]) - pos) < 0.05:
            s, e = sorted(open_floor_rules._ends(spec, p))
            out_.append((s, e))
    return out_


def minus(spans, cut):
    """The parts of `spans` no span of `cut` covers."""
    res = []
    for s, e in spans:
        pieces = [(s, e)]
        for c0, c1 in cut:
            nxt = []
            for a, b in pieces:
                if c1 <= a or c0 >= b:
                    nxt.append((a, b))
                    continue
                if a < c0:
                    nxt.append((a, c0))
                if c1 < b:
                    nxt.append((c1, b))
            pieces = nxt
        res += [(a, b) for a, b in pieces if b - a > 0.05]
    return res


def overlay(before, after, story, tx):
    g, said = ['<g id="what_moved" font-size="13" font-weight="700">'], []

    def line(axis, pos, a, b, colour, width, dash=""):
        if axis == "Y":
            x0 = x1 = tx.x(pos)
            y0, y1 = tx.y(a), tx.y(b)
        else:
            y0 = y1 = tx.y(pos)
            x0, x1 = tx.x(a), tx.x(b)
        g.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%d" stroke-linecap="round" '
                 'opacity="0.9"%s/>' % (x0, y0, x1, y1, colour, width, ' stroke-dasharray="%s"' % dash if dash else ""))
        return (x0 + x1) / 2, (y0 + y1) / 2

    def label(x, y, text, colour):
        g.append('<text x="%.1f" y="%.1f" fill="%s" stroke="#ffffff" stroke-width="4" paint-order="stroke" '
                 'text-anchor="middle">%s</text>' % (x, y, colour, floorplan._esc(text)))

    seen = set()
    for p in after.get("partitions") or []:
        if int(p.get("story", 0) or 0) != story:
            continue
        key = (p["axis"], round(float(p["pos"]), 3))
        if key in seen:
            continue
        seen.add(key)
        new = minus(covered(after, story, *key), covered(before, story, *key))
        for a, b in new:
            mx, my = line(p["axis"], key[1], a, b, "#e0242f", 9)
            said.append("new wall %s=%g %g..%g" % ("x" if p["axis"] == "Y" else "y", key[1], a, b))
    tags_before = {}
    for p in before.get("partitions") or []:
        for o in p.get("openings") or []:
            if o.get("tag"):
                tags_before[o["tag"]] = open_floor_rules._built_at(before, p, o)
    for p in after.get("partitions") or []:
        if int(p.get("story", 0) or 0) != story:
            continue
        for o in p.get("openings") or []:
            tag = o.get("tag")
            if not tag:
                continue
            at = open_floor_rules._built_at(after, p, o)
            w = float(o.get("width", 1.0))
            if tag not in tags_before:
                mx, my = line(p["axis"], float(p["pos"]), at - w / 2, at + w / 2, "#13a34a", 13)
                label(mx, my - 12, "door " + tag, "#13a34a")
                said.append("new door %s at %+.2f" % (tag, at))
            elif abs(tags_before[tag] - at) > 1e-6:
                mx, my = line(p["axis"], float(p["pos"]), at - w / 2, at + w / 2, "#f08c00", 13)
                label(mx, my + 22, "%s slid %+.2f m" % (tag, at - tags_before[tag]), "#f08c00")
                said.append("%s slid %+.2f m" % (tag, at - tags_before[tag]))
    rooms = {r["id"]: r for r in after.get("rooms") or [] if int(r.get("story", 0) or 0) == story}
    for r in rooms.values():
        was = {x["id"]: x for x in before.get("rooms") or []}.get(r["id"], {})
        for other in sorted(set(r.get("open_to") or []) - set(was.get("open_to") or [])):
            if other not in rooms:
                continue
            import tactical
            edge = tactical.open_edge(r["bounds"], rooms[other]["bounds"], layout_lint._story_parts(after, story))
            if edge is None:
                continue
            axis, pos, lo, hi, _unc = edge
            mx, my = line(axis, pos, lo, hi, "#1c64f2", 6, "10,8")
            label(mx, my - 10, "one floor: %s | %s" % (r["id"], other), "#1c64f2")
            said.append("open %s|%s" % (r["id"], other))
    g.append("</g>")
    return "\n".join(g), said


out.mkdir(parents=True, exist_ok=True)
cards = []
for name, story, caption in CASES:
    before = before_spec(name)
    after = json.loads((DC / "specs" / (name + ".json")).read_text(encoding="utf-8"))
    sb = spec_loader.spec_from_dict(before)
    sa = spec_loader.spec_from_dict(after)
    svg_b = floorplan.render_story(sb, story)
    svg_a = floorplan.render_story(sa, story)
    g, said = overlay(before, after, story, floorplan._Tx(sa))
    assert svg_a.rstrip().endswith("</svg>"), "floorplan's SVG does not end where this expects"
    svg_a = svg_a.rstrip()[:-len("</svg>")] + g + "\n</svg>\n"
    cards.append((name, story, caption, svg_b, svg_a))
    print("%-22s story %2d: %s" % (name, story, "; ".join(said) or "nothing moved"))

html = ['<!doctype html><html><head><meta charset="utf-8"><title>Open floors sorted</title><style>',
        'body{font:14px system-ui,sans-serif;margin:16px;background:#f6f5f2;color:#1d1d1f}',
        '.pair{display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:12px;margin:8px 0 28px}',
        '.pair div{background:#fff;border:1px solid #ddd;padding:6px}.pair svg{width:100%;height:auto}',
        'h2{font-size:16px;margin:18px 0 4px}.k span{display:inline-block;margin-right:14px}',
        '</style></head><body><h1 style="font-size:20px">The open floors, sorted (roadmap 260)</h1>',
        '<p class="k"><span style="color:#e0242f">&#9644; new wall</span><span style="color:#13a34a">&#9644; new door</span>'
        '<span style="color:#f08c00">&#9644; opening slid</span><span style="color:#1c64f2">- - one floor (open_to)</span></p>']
for name, story, caption, svg_b, svg_a in cards:
    html.append("<h2>%s, storey %d -- %s</h2>" % (name, story, floorplan._esc(caption)))
    html.append('<div class="pair"><div><b>Deli Counter 0.233.0</b>%s</div><div><b>0.234.0</b>%s</div></div>' % (svg_b, svg_a))
html.append("</body></html>")
(out / "plans.html").write_text("\n".join(html), encoding="utf-8")
print("wrote", out / "plans.html")
