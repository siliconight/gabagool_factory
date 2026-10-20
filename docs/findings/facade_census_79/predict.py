"""Roadmap 79, before anything is built: what three candidate bay grammars would do to the themed pool's multi-storey
enterable buildings, predicted off the built slots and the specs. Read-only; it writes nothing a build reads.

The grammars are CANDIDATES for the walker's choice, not rules this instrument holds. Each moves only UPPER-STOREY
WINDOWS that carry no gameplay tag -- every ground-floor opening, every door, breach, garage or vault, and every tagged
window stays where gameplay put it -- and keeps each storey's window count, kind and size:

  over     each upper window moves onto the centre of an opening on the storey below (after that storey's own
           moves), the nearest one not already taken, if it is within REACH; the comps' "stacked on the same bays".
  centred  the face is divided into n = round(L / BAY) equal bays, centred on the run; each upper window takes the
           nearest bay centre not already taken. The ground floor keeps its openings, so it reads as infill.
  entrance as `centred`, with the bays' phase moved so a bay centre lands on the face's primary door (a ground door
           whose tag starts `main` or `front`, else the face's widest ground opening).
  fit      the best grid the ground floor's fixed openings admit: every bay width from FIT_MIN to FIT_MAX by
           FIT_STEP, every phase that puts a bay centre on one of the face's ground openings, scored by how many of
           those openings stand on a bay centre (ties to the width nearest BAY); upper windows then as `centred`.
           It asks whether ANY one grid runs through the ground floor as gameplay laid it out.

A target is TURNED DOWN when the window's new span would leave the run (less a wall thickness at each end), come
within MIN_PIER of another opening on its storey, or cross a partition's junction with the exterior wall on its storey
(the spec's partitions whose end reaches the wall within a wall thickness; a window over a junction would have a room
wall standing in it). The window then tries the next nearest target -- DEFLECTED, counted by the reason its first
choice was turned down -- and is REFUSED, left where it is, only when no target is left. What this cannot see: stairs, fixtures and lights against the wall (a moved window needs
a refurnish, which is counted per building, not simulated), and how any of it looks.

Frame: building-local, Blender Z-up, metres; `u` along a face as in census.py.

    python docs/findings/facade_census_79/predict.py [--build DIR] [--lf DIR]
"""
import argparse
import collections
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import census  # noqa: E402

sys.path.insert(0, os.path.join(census.F, "deli_counter"))
import spec_loader  # noqa: E402  (Deli Counter's own reader: its defaults, not this file's guesses)

BAY = 3.2          # m; Deli Counter's MIDRISE_BAY, the one bay the library already chose (presets.py)
REACH = 1.6        # m; `over` moves a window at most half a bay
MIN_PIER = 0.3     # m; the least solid wall left between two openings on one storey
FIT_MIN, FIT_MAX, FIT_STEP = 2.4, 4.0, 0.1   # m; the `fit` search, a span either side of BAY
GRAMMARS = ("over", "centred", "entrance", "fit")


def _junctions(spec, story, facing):
    hx, hy = spec.footprint_x / 2.0, spec.footprint_y / 2.0
    wt = spec.wall_thick
    out = []
    for p in spec.partitions:
        if int(p.story) != story:
            continue
        a, b = sorted((float(p.start), float(p.end)))
        if p.axis == "Y" and facing in ("N", "S"):
            if (facing == "N" and b >= hy - wt) or (facing == "S" and a <= -hy + wt):
                out.append(float(p.pos))
        elif p.axis == "X" and facing in ("E", "W"):
            if (facing == "E" and b >= hx - wt) or (facing == "W" and a <= -hx + wt):
                out.append(float(p.pos))
    return out


def _span(run):
    pieces, _c = census._split_corners(run["walls"])
    allp = pieces + [(o[0], o[1], "open", 0) for o in run["openings"]]
    return min(q[0] - q[1] / 2.0 for q in allp), max(q[0] + q[1] / 2.0 for q in allp)


def _tags(bid, build):
    g = os.path.join(build, bid + ".gameplay.json")
    out = {}
    for o in json.load(open(g, encoding="utf-8")).get("openings", []) if os.path.exists(g) else []:
        out[(o["wall"], round(o["x"], 2), round(o["y"], 2))] = o.get("tag")
    return out


def _fits(t, w, others, lo, hi, wt, junctions):
    if t - w / 2.0 < lo + wt or t + w / 2.0 > hi - wt:
        return "leaves the run"
    for (u, ow) in others:
        if abs(t - u) < (w + ow) / 2.0 + MIN_PIER:
            return "too near another opening"
    for j in junctions:
        if abs(t - j) < w / 2.0 + wt / 2.0:
            return "over a partition junction"
    return None


def predict(bid, build, spec, grammar):
    _b, runs = census.building(bid, build)
    tags = _tags(bid, build)
    wt = spec.wall_thick
    res = {"movable": 0, "moved": 0, "refused": collections.Counter(), "deflected": collections.Counter(),
           "moves": [], "pairs": {}}
    finals = {}
    faces = sorted({f for (_s, f) in runs})
    for facing in faces:
        storeys = sorted(s for (s, f) in runs if f == facing)
        ground = runs.get((0, facing))
        prim = None
        if ground:
            gdoors = [o for o in ground["openings"] if o[2] == "door"]
            for o in gdoors:
                wall = "ext_0_%s" % facing
                for (wn, x, y), tag in tags.items():
                    u = x if facing in ("N", "S") else y
                    if wn == wall and abs(u - o[0]) < 0.01 and census.PRIMARY.match(str(tag or "")):
                        prim = o[0]
            if prim is None and ground["openings"]:
                prim = max(ground["openings"], key=lambda o: o[1])[0]
        grid = None
        if grammar == "fit" and ground and ground["openings"]:
            gu = [o[0] for o in ground["openings"]]
            best = None
            k = 0
            while FIT_MIN + k * FIT_STEP <= FIT_MAX + 1e-9:
                fw = FIT_MIN + k * FIT_STEP
                k += 1
                for anchor in gu:
                    score = sum(1 for g in gu if abs(((g - anchor) / fw) - round((g - anchor) / fw)) * fw
                                <= census.TOL)
                    key = (score, -abs(fw - BAY))
                    if best is None or key > best[0]:
                        best = (key, fw, anchor)
            grid = (best[1], best[2], gu)
            res["fit_aligned"] = res.get("fit_aligned", 0) + best[0][0]
            res["fit_ground"] = res.get("fit_ground", 0) + len(gu)
        for s in storeys:
            run = runs[(s, facing)]
            lo, hi = _span(run)
            junctions = _junctions(spec, s, facing)
            fixed, movable = [], []
            for (u, w, kind) in run["openings"]:
                x_y = None
                for (wn, x, y), tag in tags.items():
                    uu = x if facing in ("N", "S") else y
                    if wn == "ext_%d_%s" % (s, facing) and abs(uu - u) < 0.01:
                        x_y = tag
                if s >= 1 and kind == "window" and not x_y:
                    movable.append((u, w))
                else:
                    fixed.append((u, w))
            placed = list(fixed)
            if grammar == "over":
                below = finals.get((s - 1, facing), [])
                targets = [u for (u, _w) in below]
            else:
                L = hi - lo
                n = max(1, int(round(L / BAY)))
                bw = L / n
                targets = [lo + (i + 0.5) * bw for i in range(n)]
                if grammar == "entrance" and prim is not None:
                    k = min(range(n), key=lambda i: abs(targets[i] - prim))
                    shift = prim - targets[k]
                    targets = [t + shift for t in targets]
                    targets += [targets[0] - bw, targets[-1] + bw]
                elif grid is not None:
                    fw, anchor, _gu = grid
                    i0 = int((lo - anchor) // fw)
                    targets = [anchor + i * fw for i in range(i0 - 1, int((hi - anchor) // fw) + 2)]
            taken = set()
            for (u, w) in sorted(movable, key=lambda m: m[0]):
                res["movable"] += 1
                # `fit` stacks first: a bay with a ground-floor opening under it before one without, then nearness
                over = (lambda t: 0 if census._near(t, grid[2]) else 1) if grid is not None else (lambda t: 0)
                cands = sorted(((over(t), abs(t - u), i, t) for i, t in enumerate(targets) if i not in taken))
                cands = [(d, i, t) for (_o, d, i, t) in cands]
                if grammar == "over":
                    cands = [c for c in cands if c[0] <= REACH]
                why, best, first = "no target", None, None
                for (_d, i, t) in cands:
                    why = _fits(t, w, placed, lo, hi, wt, junctions)
                    if why is None:
                        best = (i, t)
                        break
                    first = first or why
                if best is not None and first:
                    res["deflected"][first] += 1
                if best is None:
                    res["refused"][why] += 1
                    placed.append((u, w))
                    continue
                taken.add(best[0])
                if abs(best[1] - u) > 1e-6:
                    res["moved"] += 1
                    res["moves"].append(abs(best[1] - u))
                    # a move across a partition's junction puts the window in ANOTHER ROOM
                    if any(min(u, best[1]) < j < max(u, best[1]) for j in junctions):
                        res["rehomed"] = res.get("rehomed", 0) + 1
                placed.append((best[1], w))
            finals[(s, facing)] = placed
    for (s, facing), placed in finals.items():
        below = finals.get((s - 1, facing))
        if not below:
            continue
        key = "ground" if s == 1 else "upper"
        st, n = res["pairs"].get(key, (0, 0))
        res["pairs"][key] = (st + sum(1 for (u, _w) in placed if census._near(u, [b for (b, _bw) in below])),
                             n + len(placed))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", default=os.path.join(census.F, "deli_counter", "build"))
    ap.add_argument("--lf", default=None)
    a = ap.parse_args()
    complete, _i, _n = census.bl.index(a.build)
    fit, _u = census.bl.themed_report(complete)
    specs = os.path.join(os.path.dirname(a.build.rstrip("/\\")), "specs")
    ids = []
    for e in fit:
        sp = spec_loader.load_spec(os.path.join(specs, e["id"] + ".json"))
        if getattr(sp, "facade", False):
            continue
        b, _r = census.building(e["id"], a.build)
        if max([max(f["storeys"]) + 1 for f in b["faces"].values()] or [0]) >= 2:
            ids.append((e["id"], sp))
    print("[predict] %d multi-storey enterable buildings in Level Factory's themed pool; BAY %.1f m, REACH %.1f m, "
          "MIN_PIER %.1f m" % (len(ids), BAY, REACH, MIN_PIER))
    base = {"ground": [0, 0], "upper": [0, 0]}
    for bid, _sp in ids:
        b, _r = census.building(bid, a.build)
        for f in b["faces"].values():
            for key, k in (("ground", "stack_ground"), ("upper", "stack_upper")):
                base[key][0] += f[k][0]
                base[key][1] += f[k][1]
    print("[predict] as built: stacked ground->first %d of %d, above %d of %d"
          % (base["ground"][0], base["ground"][1], base["upper"][0], base["upper"][1]))
    print()
    print("%-9s %8s %6s %8s %-22s %-40s %13s %15s %10s %8s" % (
        "grammar", "movable", "moved", "new room", "refused", "deflected", "move med/max", "stacked g->1", "above",
        "touched"))
    fa = fg = 0
    for g in GRAMMARS:
        tot = {"movable": 0, "moved": 0, "refused": collections.Counter(), "deflected": collections.Counter(),
               "moves": [],
               "pairs": {"ground": [0, 0], "upper": [0, 0]}}
        touched = 0
        for bid, sp in ids:
            r = predict(bid, a.build, sp, g)
            tot["movable"] += r["movable"]
            tot["moved"] += r["moved"]
            tot["refused"].update(r["refused"])
            tot["deflected"].update(r["deflected"])
            tot["moves"] += r["moves"]
            for key, (st, n) in r["pairs"].items():
                tot["pairs"][key][0] += st
                tot["pairs"][key][1] += n
            touched += 1 if r["moved"] else 0
            tot["rehomed"] = tot.get("rehomed", 0) + r.get("rehomed", 0)
            fa += r.get("fit_aligned", 0)
            fg += r.get("fit_ground", 0)
        mv = tot["moves"]
        print("%-9s %8d %6d %8d %-22s %-40s %6s/%-6s %7d of %-5d %4d of %-3d %4d" % (
            g, tot["movable"], tot["moved"], tot.get("rehomed", 0), ", ".join("%s %d" % kv for kv in sorted(tot["refused"].items())) or "-",
            ", ".join("%s %d" % kv for kv in sorted(tot["deflected"].items())) or "-",
            "%.2f" % statistics.median(mv) if mv else "-", "%.2f" % max(mv) if mv else "-",
            tot["pairs"]["ground"][0], tot["pairs"]["ground"][1], tot["pairs"]["upper"][0], tot["pairs"]["upper"][1],
            touched))
    print()
    print("fit: ground-floor openings standing on the best grid their own face admits, once a face: %d of %d"
          % (fa, fg))
    print()
    print("movable: upper-storey windows with no gameplay tag; moved: those the grammar moved (a window already on its")
    print("target is not a move); new room: moves across a partition's junction with the wall, into another room;")
    print("refused: no target left, the window where it is; deflected: windows whose first")
    print("target was turned down, by why, that took another; move: metres")
    print("along the face; stacked: openings over an opening on the storey below, after; touched: buildings with at")
    print("least one window moved, each of which would need a refurnish and a rebuild.")


if __name__ == "__main__":
    main()
