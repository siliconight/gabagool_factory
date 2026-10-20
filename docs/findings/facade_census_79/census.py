"""Roadmap 79's critique, measured: what a facade in Deli Counter's built library is made of, one face at a time.

Reads each building's built `<id>.slots.json` (the slot records the art pass swaps) and `<id>.gameplay.json` (the
openings' tags), Deli Counter's spec for the `facade` flag, and Level Factory's own index and themed report for which
buildings a themed lot can draw. Frame: building-local, Blender Z-up, metres. A FACE is one side (N, S, E, W) over
every storey at or above grade; basements are below grade and nobody reads them from the street. Along a face `u` is
the slot's own x (N, S) or y (E, W) -- its translation, not an offset from the run's centre -- so a storey on a
setback is compared where it stands.

Per face, and stating no cause:

  stacking   of the openings on storey s+1, how many have an opening on storey s within TOL along the face. Every
             pair of consecutive storeys that both carry openings counts; ground -> first is reported apart from the
             pairs above it, because a shop front under homes is a reason for the two to differ.
  joints     of the joints between pieces on storey s+1 (wall to wall, wall to opening; the run's two ends are not
             joints), how many continue a joint on storey s within TOL.
  remainder  the share of a face's solid wall that is a tiling remainder -- a wall slot `size_mod` "end", the corner
             posts left out; a last module that ABSORBED a sliver (`_wall_span`: an "end" at least the module wide)
             counts only its excess over the module -- and how many distinct remainder widths (to the millimetre) a
             building carries.
  pitch      per run with three or more openings, the coefficient of variation of the spacing between their centres.
  entrance   per building with an exterior door whose tag starts `main` or `front`: its width and height against the
             building's other exterior doors, whether the storey above it on its face has an opening over it, and how
             far it stands off its face's centre as a fraction of the face.

A CORNER POST is a wall slot `size_mod` "end" whose width is the wall's thickness and whose centre lies outside every
other piece of its run -- `_emit_wall_run(corners=True)` seats one at each end of an N or S run, centred on the run's
end. What this cannot see: anything the art pass adds (signs, awnings, trims, the Empties' merged sides), a
composition carried by colour or material rather than placement, and whether the result reads as designed, which is a
person's call. Openings come from the slots, so a window and its pane are one opening.

    python docs/findings/facade_census_79/census.py [--build DIR] [--lf DIR] [--json OUT]
"""
import argparse
import collections
import glob
import json
import os
import re
import statistics
import sys

F = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
_LF = sys.argv[sys.argv.index("--lf") + 1] if "--lf" in sys.argv else os.path.join(F, "level_factory")
sys.path.insert(0, _LF)
from packages.pipeline import building_library as bl  # noqa: E402

TOL = 0.05                 # m along a face: two centres or joints this close are one line
OPENING_ROLES = ("window", "doorway", "breach", "vault_door", "teller_line", "safe_deposit_boxes")
PRIMARY = re.compile(r"^(main|front)")
WALL = re.compile(r"^ext_(-?\d+)_([NSEW])$")


def _u(slot, facing):
    t = slot["transform"]["translation"]
    return t[0] if facing in ("N", "S") else t[1]


def _runs(slots):
    """{(story, facing): {"walls": [(u, w, size_mod, thick)], "openings": [(u, w, kind)]}} for storeys >= 0."""
    runs = collections.defaultdict(lambda: {"walls": [], "openings": []})
    for s in slots:
        m = WALL.match(str(s.get("wall", "")))
        if not m:
            continue
        story, facing = int(m.group(1)), m.group(2)
        if story < 0:
            continue
        dims = s["fit"]["dims"]
        u = _u(s, facing)
        if s["role"] == "wall":
            runs[(story, facing)]["walls"].append((u, dims[0], s["size_mod"], dims[1]))
        elif s["role"] in OPENING_ROLES:
            ops = s["fit"].get("openings") or [{}]
            runs[(story, facing)]["openings"].append((u, dims[0], ops[0].get("kind", s["role"])))
        else:
            raise SystemExit("UNRECOGNISED: an exterior slot of role %r (%s); the census does not know it"
                             % (s["role"], s["slot_id"]))
    return runs


def _split_corners(walls):
    """(pieces, corners): a corner post is an 'end' piece as wide as the wall is thick whose centre lies outside every
    other piece of the run."""
    if len(walls) < 3:
        return list(walls), []
    corners = []
    for wl in walls:
        u, w, mod, thick = wl
        if mod != "end" or abs(w - thick) > 1e-6:
            continue
        others = [o for o in walls if o is not wl]
        lo = min(o[0] - o[1] / 2.0 for o in others)
        hi = max(o[0] + o[1] / 2.0 for o in others)
        if u < lo - 1e-6 or u > hi + 1e-6:
            corners.append(wl)
    return [wl for wl in walls if wl not in corners], corners


def _joints(pieces):
    """Every boundary between two pieces of a run, the run's own two ends left out."""
    edges = sorted([(p[0] - p[1] / 2.0, p[0] + p[1] / 2.0) for p in pieces])
    out = []
    for (a0, a1), (b0, b1) in zip(edges, edges[1:]):
        out.append((a1 + b0) / 2.0)
    return out


def _near(x, xs):
    return any(abs(x - y) <= TOL for y in xs)


def building(bid, build_dir):
    sl = json.load(open(os.path.join(build_dir, bid + ".slots.json"), encoding="utf-8"))
    runs = _runs(sl["slots"])
    faces = collections.defaultdict(dict)
    for (story, facing), r in runs.items():
        pieces, corners = _split_corners(r["walls"])
        faces[facing][story] = {"pieces": pieces, "corners": corners, "openings": r["openings"]}
    M = float(sl.get("module_size") or 0.0)
    out = {"id": bid, "faces": {}, "remainder_widths": set(), "module_m": M, "absorbed": 0}
    for facing, storeys in sorted(faces.items()):
        f = {"storeys": sorted(storeys), "stack_ground": [0, 0], "stack_upper": [0, 0], "joints": [0, 0],
             "solid_m": 0.0, "remainder_m": 0.0, "remainders": 0, "corner_posts": 0, "pitch_cv": []}
        for st in sorted(storeys):
            r = storeys[st]
            f["corner_posts"] += len(r["corners"])
            for (u, w, mod, _t) in r["pieces"]:
                f["solid_m"] += w
                if mod == "end":
                    if M > 0 and w >= M - 1e-9:
                        out["absorbed"] += 1
                        f["remainder_m"] += w - M
                    else:
                        f["remainder_m"] += w
                    f["remainders"] += 1
                    out["remainder_widths"].add(round(w, 3))
            cs = sorted(o[0] for o in r["openings"])
            if len(cs) >= 3:
                gaps = [b - a for a, b in zip(cs, cs[1:])]
                mean = statistics.mean(gaps)
                f["pitch_cv"].append(statistics.pstdev(gaps) / mean if mean > 0 else 0.0)
            below = storeys.get(st - 1)
            if below is None:
                continue
            ups = [o[0] for o in r["openings"]]
            downs = [o[0] for o in below["openings"]]
            if ups and downs:
                key = "stack_ground" if st == 1 else "stack_upper"
                f[key][0] += sum(1 for u in ups if _near(u, downs))
                f[key][1] += len(ups)
            j_up = _joints(r["pieces"] + [(o[0], o[1], "open", 0) for o in r["openings"]])
            j_dn = _joints(below["pieces"] + [(o[0], o[1], "open", 0) for o in below["openings"]])
            f["joints"][0] += sum(1 for j in j_up if _near(j, j_dn))
            f["joints"][1] += len(j_up)
        out["faces"][facing] = f
    out["remainder_widths"] = sorted(out["remainder_widths"])
    return out, runs


def entrance(bid, build_dir, runs):
    g = os.path.join(build_dir, bid + ".gameplay.json")
    if not os.path.exists(g):
        return None
    ops = [o for o in json.load(open(g, encoding="utf-8")).get("openings", []) if o["wall"].startswith("ext")]
    doors = [o for o in ops if o["kind"] == "door"]
    prim = [o for o in doors if PRIMARY.match(str(o.get("tag") or ""))]
    if not prim:
        return {"primary": None, "doors": len(doors)}
    res = []
    for p in prim:
        m = WALL.match(p["wall"])
        story, facing = int(m.group(1)), m.group(2)
        u = p["x"] if facing in ("N", "S") else p["y"]
        others = [o for o in doors if o is not p]
        r = runs.get((story, facing))
        span = None
        if r:
            pieces, _c = _split_corners(r["walls"])
            allp = pieces + [(o[0], o[1], "open", 0) for o in r["openings"]]
            lo = min(q[0] - q[1] / 2.0 for q in allp)
            hi = max(q[0] + q[1] / 2.0 for q in allp)
            span = (lo, hi)
        above = runs.get((story + 1, facing))
        res.append({
            "tag": p["tag"], "wall": p["wall"], "width": p["width"], "height": p["height"],
            "others": len(others),
            "wider_than_all_others": bool(others) and all(p["width"] > o["width"] + 1e-6 for o in others),
            "taller_than_all_others": bool(others) and all(p["height"] > o["height"] + 1e-6 for o in others),
            "same_as_some_other": any(abs(p["width"] - o["width"]) < 1e-6 and abs(p["height"] - o["height"]) < 1e-6
                                      for o in others),
            "storey_above": above is not None,
            "opening_over_it": bool(above) and _near(u, [o[0] for o in above["openings"]]),
            "off_centre": (round(abs(u - (span[0] + span[1]) / 2.0) / (span[1] - span[0]), 3) if span else None),
        })
    return {"primary": res, "doors": len(doors)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", default=os.path.join(F, "deli_counter", "build"))
    ap.add_argument("--lf", default=None)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    complete, _incomplete, _non = bl.index(a.build)
    fit, _unfit = bl.themed_report(complete)
    pool = {e["id"] for e in fit}
    specs = os.path.join(os.path.dirname(a.build.rstrip("/\\")), "specs")
    ids = sorted(os.path.basename(p)[:-len(".slots.json")] for p in glob.glob(os.path.join(a.build, "*.slots.json")))
    rows = []
    for bid in ids:
        spec = os.path.join(specs, bid + ".json")
        facade = bool(json.load(open(spec, encoding="utf-8")).get("facade")) if os.path.exists(spec) else None
        b, runs = building(bid, a.build)
        b["facade"] = facade
        b["pool"] = bid in pool
        b["entrance"] = entrance(bid, a.build, runs)
        b["storeys"] = max([max(f["storeys"]) + 1 for f in b["faces"].values()] or [0])
        rows.append(b)

    def tot(group, key):
        s = [0, 0]
        for b in group:
            for f in b["faces"].values():
                s[0] += f[key][0]
                s[1] += f[key][1]
        return s

    def pct(p):
        return "%5.1f %%" % (100.0 * p[0] / p[1]) if p[1] else "    -  "

    print("[census] Deli Counter build %s: %d buildings with slots; Level Factory %s's themed pool %d of %d indexed"
          % (a.build, len(rows), open(os.path.join(_LF, "VERSION"), encoding="utf-8").read().strip(), len(pool),
             len(complete)))
    print("[census] TOL %.2f m along a face; storeys >= 0; a face is one side over all its storeys" % TOL)
    groups = [("themed pool (enterable)", [b for b in rows if b["pool"] and not b["facade"]]),
              ("Empties (facade; preset bays)", [b for b in rows if b["facade"]]),
              ("outside the pool, enterable", [b for b in rows if not b["pool"] and not b["facade"]])]
    assert sum(len(g) for _n, g in groups) == len(rows), "a building in no group"
    assert not [b for b in rows if b["pool"] and b["facade"]], "an Empty in the themed pool: the groups need a row" 
    print()
    print("%-32s %5s %9s %9s %9s %9s %10s" % ("group", "bldgs", "multi-st", "stack g>1", "stack up", "joints",
                                               "remainder"))
    for name, grp in groups:
        multi = [b for b in grp if b["storeys"] >= 2]
        solid = sum(f["solid_m"] for b in grp for f in b["faces"].values())
        rem = sum(f["remainder_m"] for b in grp for f in b["faces"].values())
        print("%-32s %5d %9d %9s %9s %9s %9.1f %%" % (name, len(grp), len(multi), pct(tot(grp, "stack_ground")),
                                                    pct(tot(grp, "stack_upper")), pct(tot(grp, "joints")),
                                                    100.0 * rem / solid if solid else 0.0))
    print()
    print("stack g>1: of the first storey's openings, the share with a ground-floor opening under them (within TOL);")
    print("stack up: the same for every pair of storeys above; joints: of the joints between pieces on a storey, the")
    print("share that continue a joint on the storey below; remainder: the share of solid wall length that is a tiling")
    print("remainder (corner posts left out).")

    print()
    print("THE THEMED POOL'S ENTERABLE BUILDINGS, one row a building (multi-storey first):")
    print("%-26s %3s %6s %6s %6s %6s %5s %-38s" % ("building", "st", "stk g1", "stk up", "joint", "rem", "widths",
                                                    "entrance (tag: w x h vs others; over it; off centre)"))
    ent = collections.Counter()
    for b in sorted(groups[0][1], key=lambda b: (-b["storeys"], b["id"])):
        solid = sum(f["solid_m"] for f in b["faces"].values())
        rem = sum(f["remainder_m"] for f in b["faces"].values())
        e = b["entrance"] or {}
        if e.get("primary"):
            p = e["primary"][0]
            mark = ("wider" if p["wider_than_all_others"] else ("same" if p["same_as_some_other"] else "differs"))
            if not p["others"]:
                mark = "only door"
            et = "%s: %.2fx%.2f %s; %s; %.2f" % (p["tag"], p["width"], p["height"], mark,
                                                 ("over" if p["opening_over_it"] else
                                                  ("no" if p["storey_above"] else "1 st")), p["off_centre"] or 0.0)
            ent["has a primary"] += 1
            ent["primary %s" % mark] += 1
            if p["storey_above"]:
                ent["with a storey above"] += 1
                ent["an opening over it" if p["opening_over_it"] else "nothing over it"] += 1
            if p["off_centre"] is not None and p["off_centre"] <= 0.05:
                ent["on its face's centre (<= 5 %)"] += 1
        else:
            et = "none tagged main/front (%d doors)" % e.get("doors", 0)
            ent["no primary tagged"] += 1
        print("%-26s %3d %6s %6s %6s %5.1f%% %5d  %s" % (
            b["id"], b["storeys"], pct(tot([b], "stack_ground")).strip(), pct(tot([b], "stack_upper")).strip(),
            pct(tot([b], "joints")).strip(), 100.0 * rem / solid if solid else 0.0, len(b["remainder_widths"]), et))
    print()
    print("entrances in the pool's enterable buildings:", dict(sorted(ent.items())))
    cvs = [cv for b in groups[0][1] for f in b["faces"].values() for cv in f["pitch_cv"]]
    if cvs:
        print("opening pitch, runs with 3+ openings in the pool's enterable buildings: %d runs, median CV %.2f, "
              "%d regular (CV < 0.05)" % (len(cvs), statistics.median(cvs), sum(1 for c in cvs if c < 0.05)))
    widths = collections.Counter(w for b in groups[0][1] for w in b["remainder_widths"])
    print("distinct remainder widths across the pool's enterable buildings: %d; the commonest: %s"
          % (len(widths), ", ".join("%.3f x%d" % kv for kv in widths.most_common(8))))
    if a.json:
        with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(rows, fh, indent=1, sort_keys=True)
        print("[census] wrote", a.json)


if __name__ == "__main__":
    main()
