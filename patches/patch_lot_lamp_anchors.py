"""Lot 0.79.0 -- a streetlight anchor stands on the pole that stands there.

Anchored patch. Asserts every source block it replaces matches exactly once
and refuses to write on a miss (CLAUDE.md, Grounding).

WHY. `pole_vs_light.gd` on cold run 9087's walk copy:

    POLE/LIGHT: 54 streetlight light(s), 48 streetlight prop mesh(es)
       min 3.50 m   median 24.93 m   mean 30.62 m   max 93.68 m
       lights with a pole within 1.0 m: 0 of 54

Two functions in ONE repo put streetlights on a site and neither read the
other. `site_furniture.plan_furniture` stands `streetlight` cover pieces
along the kerb bands; `lot._streetlight_anchors` derived light rows from the
PATH graph and from a ring 2 m inside the ground rect. Nothing tied them
together, so every exterior light in the level was light from nowhere.
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOT = ROOT / "lot" / "lot.py"


def _apply(path, pairs):
    raw = path.read_bytes()
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    if crlf not in (0, lf):
        raise SystemExit(f"REFUSED: {path} has mixed line endings "
                         f"({crlf} CRLF of {lf} LF)")
    eol = "\r\n" if crlf else "\n"
    text = raw.decode("utf-8")
    if eol == "\r\n":
        text = text.replace("\r\n", "\n")
    for i, (old, new) in enumerate(pairs):
        n = text.count(old)
        if n != 1:
            raise SystemExit(f"REFUSED: anchor {i} matches {n} times, not 1")
        text = text.replace(old, new, 1)
    out = text.replace("\n", eol) if eol == "\r\n" else text
    path.write_bytes(out.encode("utf-8"))
    print(f"[patch] {path.name}: {len(pairs)} block(s), "
          f"{len(raw)} -> {len(out.encode('utf-8'))} bytes, eol={eol!r}")


CONST_OLD = '''STREETLIGHT_H = 6.0        # pole-top height (Blender Z-up metres)
'''

CONST_NEW = '''#: How far the lamp POINT sits below the top of a streetlight slot module,
#: in metres. Derived from `zoo/zoo_keeper/recipes/streetlight.py`, which
#: builds the species centred and takes two placements: at an ANCHOR the
#: pole top is the anchor and the head floats above it, but in a SLOT
#: (`fit_exact`, which is how the site kit stands these poles) the module is
#: exactly `h` tall -- the pole top is at local `h/2 - 0.18`, the shoebox
#: head fills the last 0.18 to the module's top, and the emissive lens
#: protrudes to local `h/2 - 0.175`. A light at the module top would be
#: inside the head, and the head would shadow its own spot.
#:
#: Zoo's `tests/test_streetlight_lens_drop.py` asserts the recipe still puts
#: the lens there, so moving it fails Zoo's suite rather than silently
#: burying this site's street lighting inside 48 shoeboxes.
STREETLIGHT_LENS_DROP = 0.175
'''

FN_OLD = '''def _streetlight_anchors(site_spec):
    """Exterior lights Lot owns (Deli Counter can\'t see the outdoors): a
    streetlight row down each path, and a ring around the ground perimeter."""
    anchors = []
    bmap = {b["id"]: b for b in site_spec["buildings"]}

    for i, p in enumerate(site_spec.get("paths", [])):
        a = bmap[p["from"]]["at"] if "from" in p else p["a"]
        b2 = bmap[p["to"]]["at"] if "to" in p else p["b"]
        (ax, ay), (bx, by) = a, b2
        length = math.hypot(bx - ax, by - ay)
        if length < 1e-3:
            continue
        count = max(2, min(8, round(length / 10.0)))
        anchors.append({
            "id": "site/path_%d_lights" % i, "type": "streetlight",
            "source": "derived", "building": None,
            "pos": [round((ax + bx) / 2, 3), round((ay + by) / 2, 3), STREETLIGHT_H],
            "rot_y": round(math.degrees(math.atan2(by - ay, bx - ax)) % 360, 3),
            "row": {"count": count, "spacing": round(length / count, 3)},
            "reacts_to_alarm": False,
        })

    import site_extent
    rect = site_extent.resolve(site_spec).rect
    if rect:
        x0, y0, x1, y1 = rect
        cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        span_x, span_y = x1 - x0, y1 - y0
        inset = 2.0
        # (name, x, y, rot_y, span-along-the-edge)
        edges = [
            ("s", cx, y0 + inset, 0.0, span_x),
            ("n", cx, y1 - inset, 0.0, span_x),
            ("w", x0 + inset, cy, 90.0, span_y),
            ("e", x1 - inset, cy, 90.0, span_y),
        ]
        for name, x, y, rot, span in edges:
            count = max(2, min(10, round(span / 15.0)))
            anchors.append({
                "id": "site/perimeter_%s_lights" % name, "type": "streetlight",
                "source": "derived", "building": None,
                "pos": [round(x, 3), round(y, 3), STREETLIGHT_H], "rot_y": rot,
                "row": {"count": count, "spacing": round(span / count, 3)},
                "reacts_to_alarm": False,
            })
    return anchors
'''

FN_NEW = '''def _streetlight_anchors(site_spec):
    """One exterior light per streetlight POLE the site actually stands.

    LIGHT COMES FROM A LAMP, and until 0.79.0 none of this site\'s did. Two
    functions in this one repo put streetlights on a site and neither read
    the other: `site_furniture.plan_furniture` stands `streetlight` cover
    pieces along the kerb bands, nudged clear of the dropped kerbs and the
    mission markers, while this function derived light ROWS from the path
    graph and from a ring 2 m inside the ground rect. Measured on cold run
    9087\'s walk copy with `pole_vs_light.gd`:

        54 streetlight lights, 48 streetlight props; nearest pole to a
        light min 3.50 m, median 24.93 m, mean 30.62 m, max 93.68 m --
        0 of 54 lights had a pole within 1.0 m.

    The walker, standing at the map edge in a cone of it: "a reminder that
    light should comes from light sources, i don\'t know where this light is
    coming from".

    So the poles ARE the anchors. `merge_lights` runs after
    `plan_furniture` has extended `site_spec["cover"]` (see the build order
    in `write_site`), and each lamp piece carries its plan point, its yaw
    and its height -- so pole and light are coincident by construction
    rather than by two formulas happening to agree.

    WHAT WENT AWAY WITH THE ROWS, said rather than discovered later:

    * the perimeter ring lit the boundary wall from nothing, which is the
      frame the walker was standing in. The map edge is now lit by the moon
      alone. Standing poles out there is a placement decision for
      `site_furniture`, not something to fake from the light side.
    * the path rows lit the path GRAPH, which is not where the street
      furniture is -- that is the 24.93 m median above.
    * a site whose roads carry no sidewalk stands no lamps, so it now gets
      no exterior lights at all. `write_site` says that out loud
      (`LOT_NO_EXTERIOR_LIGHTS`) instead of papering over it with a row,
      because the row is the defect.
    """
    anchors = []
    for i, cv in enumerate(site_spec.get("cover") or []):
        if cv.get("species") != "streetlight":
            continue
        dims = cv.get("dims") or []
        if len(dims) < 3:
            continue
        h = float(dims[2])
        # the same base `write_site_slots` stands the module on, so the
        # light is placed against the pole as built and not against grade
        base = SIDEWALK_H if cv.get("base") == "sidewalk" else 0.0
        x, y = cv["at"]
        anchors.append({
            # the pole\'s own name, so an id names a thing in the scene and
            # Lux\'s every-third-pole ballast buzz keys to a real lamp
            "id": "site/%s" % str(cv.get("name") or ("lamp_%d" % i)).lower(),
            "type": "streetlight",
            "source": "site_furniture",
            "building": None,
            # THE LENS, NOT THE POLE TOP. Lux reads `pos[2]` as the lamp\'s
            # height above the road to derive its energy, and that is still
            # what this is -- 0.175 m less than it was, which is the head.
            "pos": [round(float(x), 3), round(float(y), 3),
                    round(base + h - STREETLIGHT_LENS_DROP, 3)],
            "rot_y": round(float(cv.get("yaw") or 0.0) % 360.0, 3),
            # ONE LAMP, ONE LIGHT. A row cannot describe these: `_nudged`
            # moves a pole clear of a kerb cut or a marker, so the spacing
            # along a kerb is not constant and a {count, spacing} pair
            # would put most of the lights back off the poles again.
            "row": {"count": 1, "spacing": 0.0},
            # THE HARDWARE ALREADY STANDS, and names which slot stands it.
            # Zoo\'s fixture pass builds a pole at every `streetlight`
            # anchor it is given (`core/fixtures.py`); without this it
            # would stand a second pole inside this one the day a
            # site-level fixture job exists. `plan_fixtures` skips an
            # anchor carrying this field and records the reason.
            "hardware": "slot:cover_%d" % i,
            "reacts_to_alarm": False,
        })
    return anchors
'''

CALL_OLD = '''    print(f"[lot] site lights -> {lights_out} "
          f"({len(merged_lights[\'anchors\'])} anchors)")
'''

CALL_NEW = '''    print(f"[lot] site lights -> {lights_out} "
          f"({len(merged_lights[\'anchors\'])} anchors)")
    # EVERY EXTERIOR LIGHT STANDS ON A LAMP, or the site has none and says
    # so. `_streetlight_anchors` derives these from the poles
    # `plan_furniture` placed, so a site whose roads carry no sidewalk band
    # carries no street lighting -- which is a real state worth printing,
    # not one to fill in with a row of lights from nowhere (0.79.0).
    _lamps = [a for a in merged_lights["anchors"]
              if a.get("type") == "streetlight"]
    if _lamps:
        print(f"[lot] LOT_STREETLIGHTS_LIT: {len(_lamps)} lamp(s), "
              f"each on the pole its slot stands")
    else:
        print("[lot] LOT_NO_EXTERIOR_LIGHTS: no streetlight pole on this "
              "site, so nothing lights the street; the moon and the "
              "buildings\' own facade lights are all there is")
'''


def main():
    if not LOT.exists():
        raise SystemExit(f"REFUSED: {LOT} not found")
    _apply(LOT, [(CONST_OLD, CONST_NEW), (FN_OLD, FN_NEW),
                 (CALL_OLD, CALL_NEW)])
    return 0


if __name__ == "__main__":
    sys.exit(main())
