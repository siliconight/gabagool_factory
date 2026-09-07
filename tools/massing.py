"""How prism-like is a building? Roadmap 116.

    python tools/massing.py                    # every built shell
    python tools/massing.py night_pawn bank    # named shells
    python tools/massing.py --detail night_pawn

WHY. Every improvement this pipeline has learned in a year -- Pixelcoat
themes, macro-structure skins, Patina layering, the texel-density work of
items 79/104/108 -- happens on the SURFACE of a rectangular prism. From across
a street the buildings are still boxes, and a street of boxes reads as
generated however good each wall looks up close. That is item 18's "works vs
good" gap measured on SILHOUETTE rather than on texture, and until there is a
number for it, "less boxy" is a matter of opinion and will be argued rather
than measured.

WHAT IT MEASURES, and neither number is a judgement.

  fill      The silhouette's area divided by its own bounding box, per
            elevation. A rectangular prism viewed square-on fills its
            bounding box exactly, so a prism scores 1.000 and anything that
            steps, sets back or projects scores less. Reported for the two
            orthogonal elevations (looking along -Y and along -X).

  masses    How many DISTINCT horizontal footprints the exterior walls
            describe, one sample per storey. A single extruded rectangle
            describes one. Two means the building steps once.

WHAT IT READS. `build/<shell>.slots.json` -- every slot is an axis-aligned box
with a centre and dims, which is exactly what a silhouette needs, and it is
already on disk. Coordinates are the manifest's own: spec/Blender Z-up.

WHAT IT DOES NOT SEE, said plainly because an instrument that hides its blind
spot is worse than none. Parapets and fire escapes are not slots, so this is
the MASS and not the roofline. That bias runs one way -- both of those ADD
relief, so excluding them can only make a building look MORE prism-like than
it is. A shell scoring 1.000 here is a prism whatever they add on top; a shell
scoring below 1.000 would score lower still if they were counted.

It prints what it measured and stops. What fill ratio is "good enough" is a
design question, and it belongs in the reply.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(os.path.dirname(HERE), "deli_counter", "build")

CELL = 0.10          # m, silhouette raster
STOREY_EPS = 0.01    # m, footprint comparison tolerance


def _shell_boxes(slots):
    """The OUTER shell's boxes as (x0, y0, z0, x1, y1, z1).

    Exterior wall segments and the roof. Interior partitions, floors,
    ceilings and props sit inside the envelope and cannot change the outline.

    APERTURES ARE EXCLUDED BECAUSE THEY ARE VOIDS. A doorway or window slot
    marks a hole in the wall plane, not a solid, and counting one as a box was
    this tool's first bug. Dropping them loses nothing: the wall plane they
    sit in is already counted.
    """
    out = []
    for s in slots:
        sid = s.get("slot_id", "")
        role = s.get("role")
        if not (sid.startswith("ext_") or role == "roof"):
            continue
        if role in ("doorway", "window", "breach"):
            continue          # an aperture is a VOID; it adds no mass
        tr = s.get("transform") or {}
        t_ = tr.get("translation")
        d = (s.get("fit") or {}).get("dims")
        if not t_ or not d:
            continue
        cx, cy, cz = (float(v) for v in t_)
        sx, sy, sz = (float(v) for v in d)
        # `fit.dims` IS MODULE-LOCAL and `rot_y` turns it -- one convention
        # for every slot since Deli Counter 0.109.0 (roadmap 119). Before
        # that, wall segments carried WORLD dims while apertures carried
        # local ones, and this tool's first version read the world reading
        # into both.
        rot = int(round(float(tr.get("rot_y") or 0.0))) % 180
        if rot == 90:
            sx, sy = sy, sx
        out.append((cx - sx / 2, cy - sy / 2, cz - sz / 2,
                    cx + sx / 2, cy + sy / 2, cz + sz / 2))
    return out


def _storey_extent(boxes, story_height, k):
    """(x0, y0, x1, y1) of the wall boxes standing on storey `k`, or None."""
    z = (k + 0.5) * story_height
    cut = [b for b in boxes if b[2] <= z <= b[5]]
    if not cut:
        return None
    return (min(b[0] for b in cut), min(b[1] for b in cut),
            max(b[3] for b in cut), max(b[4] for b in cut))


def _mass_blocks(boxes, story_height, floor_thick, base, n_stories):
    """The building's MASS as one block per storey, plus its slab bands.

    A SILHOUETTE IS AN OUTLINE, not a wall elevation, and that distinction is
    this tool's second bug rather than a nicety. Summing individual wall
    segments leaves every doorway and window as a hole, so a shell scored
    0.963 against its own bounding box for apertures -- interior detail that
    has nothing to do with whether the building is a box, and that would
    penalise a well-fenestrated facade exactly like a genuine setback. One
    block per storey, taken from that storey's own wall extents, asks the
    question that was meant: does the mass CHANGE with height.

    The slab bands are here for the opposite reason -- they are real and the
    manifest cannot see them. Its `floor` and `ceiling` entries are 0.02 m
    skins; the structural slab is `floor_thick` and is recorded as no slot.
    Measured on `night_pawn`: two missing bands of 0.25 m over a 6.80 m
    elevation is 7.4%.

    EVERY BLOCK TAKES ITS OWN STOREY'S EXTENT rather than the spec's
    footprint, which matters for exactly the thing this tool exists to find:
    a stepped building's slabs step with it, and synthesising them at the full
    footprint would fill the step back in and hide it.
    """
    out = []
    for k in range(base, base + n_stories):
        ext = _storey_extent(boxes, story_height, k)
        if ext is None:
            continue
        z0 = k * story_height
        out.append((ext[0], ext[1], z0 - floor_thick, ext[2], ext[3],
                    z0 + story_height))
    return out


def _fill(boxes, a, b):
    """Silhouette area / bounding-box area, projecting onto axes (a, b).

    Rasterised rather than solved analytically: the boxes overlap heavily at
    every corner and mitre, and a union of rectangles is where an
    inclusion-exclusion sum quietly double-counts. A grid cannot.
    """
    if not boxes:
        return None
    lo_a = min(bx[a] for bx in boxes)
    hi_a = max(bx[a + 3] for bx in boxes)
    lo_b = min(bx[b] for bx in boxes)
    hi_b = max(bx[b + 3] for bx in boxes)
    na = max(1, int(round((hi_a - lo_a) / CELL)))
    nb = max(1, int(round((hi_b - lo_b) / CELL)))
    if na * nb > 4_000_000:
        return None                      # refuse rather than take an hour
    grid = bytearray(na * nb)
    for bx in boxes:
        i0 = max(0, int((bx[a] - lo_a) / CELL))
        i1 = min(na, int(round((bx[a + 3] - lo_a) / CELL)))
        j0 = max(0, int((bx[b] - lo_b) / CELL))
        j1 = min(nb, int(round((bx[b + 3] - lo_b) / CELL)))
        for j in range(j0, j1):
            row = j * na
            for i in range(i0, i1):
                grid[row + i] = 1
    return sum(grid) / float(na * nb)


def _masses(boxes, story_height, n_stories, base):
    """Distinct horizontal footprints, one sample per storey."""
    seen = []
    for k in range(base, base + n_stories):
        ext = _storey_extent(boxes, story_height, k)
        if ext is None:
            continue
        r = tuple(round(v, 2) for v in ext)
        if not any(all(abs(r[i] - p[i]) <= STOREY_EPS for i in range(4))
                   for p in seen):
            seen.append(r)
    return seen


def measure(path):
    with open(path, encoding="utf-8") as f:
        man = json.load(f)
    slots = man.get("slots") or []
    boxes = _shell_boxes(slots)
    stem = os.path.splitext(os.path.basename(path))[0]
    stem = stem[:-len(".slots")] if stem.endswith(".slots") else stem
    spec_path = os.path.join(os.path.dirname(os.path.dirname(path)),
                             "specs", stem + ".json")
    sh, ns, base, fx, fy, ft = 3.4, 1, 0, None, None, 0.25
    if os.path.exists(spec_path):
        with open(spec_path, encoding="utf-8") as f:
            sp = json.load(f)
        sh = float(sp.get("story_height") or 3.4)
        ns = int(sp.get("n_stories") or 1)
        base = -1 if sp.get("has_basement") else 0
        ns += 1 if sp.get("has_basement") else 0
        fx, fy = sp.get("footprint_x"), sp.get("footprint_y")
        ft = float(sp.get("floor_thick") or 0.25)
    if not boxes:
        # A NON-MODULAR SHELL EMITS NO WALL SLOTS -- `modular` unset means
        # `_emit_wall_run` never runs, so the manifest carries props and
        # nothing else. 15 of the library's 129 are built this way, and they
        # include most of the hand-authored heist levels, so dropping them
        # would quietly exclude the most interesting population.
        #
        # The spec still answers the question, and answers it by
        # CONSTRUCTION: `LevelSpec` carries ONE `footprint_x`, ONE
        # `footprint_y` and ONE `n_stories`, so a shell built from it cannot
        # be anything but a single extruded rectangle. Reported as source
        # `spec` with no fill, because "1.000" derived from a spec that cannot
        # express another answer would be a measurement of nothing.
        if not fx or not fy:
            return None
        return {"shell": stem, "stories": ns, "source": "spec",
                "fill_y": None, "fill_x": None,
                "masses": [(-fx / 2, -fy / 2, fx / 2, fy / 2)], "boxes": 0}
    solid = _mass_blocks(boxes, sh, ft, base, ns) + [
        b for b in boxes if b[5] > (base + ns) * sh - 1e-9]   # + the roof cap
    return {
        "shell": stem,
        "stories": ns,
        "source": "slots",
        "fill_y": _fill(solid, 0, 2),     # elevation looking along -Y (X,Z)
        "fill_x": _fill(solid, 1, 2),     # elevation looking along -X (Y,Z)
        "masses": _masses(boxes, sh, ns, base),
        "boxes": len(boxes),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("shells", nargs="*", help="shell stems; default all")
    ap.add_argument("--detail", action="store_true",
                    help="list each distinct footprint")
    ap.add_argument("--build", default=BUILD)
    a = ap.parse_args(argv)

    paths = ([os.path.join(a.build, s + ".slots.json") for s in a.shells]
             if a.shells else sorted(glob.glob(os.path.join(a.build,
                                                            "*.slots.json"))))
    paths = [p for p in paths if os.path.exists(p)]
    if not paths:
        print("massing: no slot manifests under %s" % a.build)
        return 1

    rows = []
    for p in paths:
        m = measure(p)
        if m:
            rows.append(m)
    if not rows:
        print("massing: %d manifest(s) read, none carried an outer shell"
              % len(paths))
        return 1

    print("%-44s %6s %7s %7s %7s  %s" % ("shell", "story", "fill-Y",
                                        "fill-X", "masses", "from"))
    for m in sorted(rows, key=lambda r: (min(r["fill_y"] or 1, r["fill_x"] or 1),
                                         r["shell"])):
        print("%-44s %6d %7s %7s %7d  %s"
              % (m["shell"], m["stories"],
                 "-" if m["fill_y"] is None else "%.3f" % m["fill_y"],
                 "-" if m["fill_x"] is None else "%.3f" % m["fill_x"],
                 len(m["masses"]), m["source"]))
        if a.detail:
            for x0, y0, x1, y1 in m["masses"]:
                print("        footprint x %.2f..%.2f  y %.2f..%.2f"
                      % (x0, x1, y0, y1))

    prisms = [m for m in rows if len(m["masses"]) <= 1]
    full = [m for m in rows
            if (m["fill_y"] or 0) >= 0.995 and (m["fill_x"] or 0) >= 0.995]
    print()
    meas = [m for m in rows if m["source"] == "slots"]
    print("%d shell(s): %d measured from built geometry, %d from the spec "
          "alone (non-modular: no wall slots to measure)"
          % (len(rows), len(meas), len(rows) - len(meas)))
    print("  %d describe ONE footprint (a single extruded rectangle)"
          % len(prisms))
    print("  %d fill their own bounding box to within 0.5%% on BOTH elevations"
          % len(full))
    if rows:
        fy = [m["fill_y"] for m in meas if m["fill_y"] is not None]
        fx = [m["fill_x"] for m in meas if m["fill_x"] is not None]
        if fy and fx:
            print("  fill-Y  min %.3f  mean %.3f      fill-X  min %.3f  "
                  "mean %.3f" % (min(fy), sum(fy) / len(fy),
                                 min(fx), sum(fx) / len(fx)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
