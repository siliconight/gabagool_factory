"""Roadmap 79, before anything is built: what candidate bay grammars would do to the themed pool's multi-storey
enterable buildings, predicted off the built slots and the specs. Read-only; it writes nothing a build reads.

The grammars are CANDIDATES for the walker's choice, not rules this instrument holds. Each moves only UPPER-STOREY
WINDOWS that carry no gameplay tag -- every ground-floor opening, every door, breach, garage or vault, and every tagged
window stays where gameplay put it -- and keeps each storey's window count, kind and size:

  over     each upper window moves onto the centre of an opening on the storey below (after that storey's own
           moves), the nearest one not already taken, if it is within the row's reach; the comps' "stacked on the
           same bays". Rows at half a bay, a bay, and 6 m.
  over sym as `over` at a bay's reach, keeping the symmetry the upper storeys were authored with: a window with a
           partner mirrored about the face's centre moves only with it, onto two openings below that are each
           other's mirror, both within reach; a window on the centre line moves only onto an opening below on it;
           any other window as `over`.
  centred  the face is divided into n = round(L / BAY) equal bays, centred on the run; each upper window takes the
           nearest bay centre not already taken. The ground floor keeps its openings, so it reads as infill.
  entrance as `centred`, with the bays' phase moved so a bay centre lands on the face's primary door (a ground door
           whose tag starts `main` or `front`, else the face's widest ground opening).
  fit      the best grid the ground floor's fixed openings admit: every bay width from FIT_MIN to FIT_MAX by
           FIT_STEP, every phase that puts a bay centre on one of the face's ground openings, scored by how many of
           those openings stand on a bay centre (ties to the width nearest BAY); upper windows then take a bay with a
           ground opening under it first, then the nearest. It asks whether ANY one grid runs through the ground
           floor as gameplay laid it out.

A target is TURNED DOWN when the window's new span would leave the run (less a wall thickness at each end), come
within MIN_PIER of another opening on its storey, or cross a partition's junction with the exterior wall on its storey
(the spec's partitions whose end reaches the wall within a wall thickness; a window over a junction would have a room
wall standing in it). The window then tries the next nearest target -- DEFLECTED, counted by the reason its first
choice was turned down -- and is REFUSED, left where it is, only when no target is left. A move whose path crosses a
junction puts the window in ANOTHER ROOM, counted. MIRRORED counts, per storey, the openings with a partner mirrored
about the face's centre within TOL -- the symmetry a grammar can cost while it stacks.

What this cannot see: stairs, fixtures and lights against the wall (a moved window needs a refurnish, which is counted
per building, not simulated), and how any of it looks.

REFUTED, and kept: the first version priced `over` at half a bay only (1.6 m: 17 windows moved, 45 of 169 stacked), and
the finding concluded from it that moving the upper storeys alone cannot compose a face. At one bay's reach the same
grammar moves 71 and stacks 99, no window changing room (the README, above the result that replaced it).

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
MIN_PIER = 0.3     # m; the least solid wall left between two openings on one storey
FIT_MIN, FIT_MAX, FIT_STEP = 2.4, 4.0, 0.1   # m; the `fit` search, a span either side of BAY
#: (label, grammar, reach in m -- `over` only)
ROWS = (("over 1.6", "over", BAY / 2.0), ("over 3.2", "over", BAY), ("over 6.0", "over", 6.0),
        ("over sym", "over_sym", BAY), ("centred", "centred", None), ("entrance", "entrance", None),
        ("fit", "fit", None))


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


def _tag_at(tags, wall, facing, u):
    for (wn, x, y), tag in tags.items():
        if wn == wall and abs((x if facing in ("N", "S") else y) - u) < 0.01:
            return tag
    return None


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


def _mirrored(us, centre):
    return sum(1 for u in us if census._near(2.0 * centre - u, us))


def _fit_grid(gu):
    best = None
    k = 0
    while FIT_MIN + k * FIT_STEP <= FIT_MAX + 1e-9:
        fw = FIT_MIN + k * FIT_STEP
        k += 1
        for anchor in gu:
            score = sum(1 for g in gu if abs(((g - anchor) / fw) - round((g - anchor) / fw)) * fw <= census.TOL)
            key = (score, -abs(fw - BAY))
            if best is None or key > best[0]:
                best = (key, fw, anchor)
    return best[1], best[2], best[0][0]


def _over_sym(movable, below, fixed, centre, reach, lo, hi, wt, junctions, res):
    """`over sym` for one storey: the windows' final (u, w), counting into `res` as `predict` does."""
    out, done = [], set()
    pairs = []
    for i, (u, w) in enumerate(movable):
        if i in done:
            continue
        if census._near(u, [centre]):
            pairs.append(((i,), (u,), w))
            done.add(i)
            continue
        j = next((j for j, (v, wv) in enumerate(movable)
                  if j != i and j not in done and census._near(v, [2.0 * centre - u]) and abs(wv - w) < 1e-6), None)
        if j is None:
            pairs.append(((i,), (u,), w))
            done.add(i)
        else:
            pairs.append(((i, j), (u, movable[j][0]), w))
            done.update((i, j))
    taken = set()
    for (idx, us, w) in pairs:
        res["movable"] += len(idx)
        if len(us) == 2:
            u = min(us)
            cands = sorted((abs(b - u), b) for b in below
                           if b < centre and census._near(2.0 * centre - b, below) and abs(b - u) <= reach + 1e-9)
            tgt = [(b, 2.0 * centre - b) for (_d, b) in cands]
        elif census._near(us[0], [centre]):
            tgt = [(b,) for b in below if census._near(b, [centre])]
        else:
            tgt = [(b,) for (_d, b) in sorted((abs(b - us[0]), b) for b in below if abs(b - us[0]) <= reach + 1e-9)]
        best = None
        for ts in tgt:
            if any(round(x, 3) in taken for x in ts):
                continue
            others = list(fixed) + out
            if all(_fits(x, w, others + [(y, w) for y in ts if y is not x], lo, hi, wt, junctions) is None
                   for x in ts):
                best = ts
                break
        if best is None:
            res["refused"]["no target" if not tgt else "turned down"] += len(idx)
            out += [(u, w) for u in us]
            continue
        for (u, x) in zip(sorted(us), sorted(best)):
            taken.add(round(x, 3))
            if abs(x - u) > 1e-6:
                res["moved"] += 1
                res["moves"].append(abs(x - u))
                if any(min(u, x) < j < max(u, x) for j in junctions):
                    res["rehomed"] += 1
            out.append((x, w))
    return out


def predict(bid, build, spec, grammar, reach=None):
    """One building under one grammar: the counts, and the final positions per (storey, face)."""
    _b, runs = census.building(bid, build)
    tags = _tags(bid, build)
    wt = spec.wall_thick
    res = {"movable": 0, "moved": 0, "rehomed": 0, "refused": collections.Counter(),
           "deflected": collections.Counter(), "moves": [], "pairs": {}, "mirrored": [0, 0], "mirrored_built": [0, 0],
           "fit_aligned": 0, "fit_ground": 0}
    finals = {}
    for facing in sorted({f for (_s, f) in runs}):
        storeys = sorted(s for (s, f) in runs if f == facing)
        ground = runs.get((0, facing))
        prim = None
        if ground:
            for o in ground["openings"]:
                if o[2] == "door" and census.PRIMARY.match(str(_tag_at(tags, "ext_0_%s" % facing, facing, o[0]) or "")):
                    prim = o[0]
            if prim is None and ground["openings"]:
                prim = max(ground["openings"], key=lambda o: o[1])[0]
        grid = None
        if grammar == "fit" and ground and ground["openings"]:
            gu = [o[0] for o in ground["openings"]]
            fw, anchor, score = _fit_grid(gu)
            grid = (fw, anchor, gu)
            res["fit_aligned"] += score
            res["fit_ground"] += len(gu)
        for s in storeys:
            run = runs[(s, facing)]
            lo, hi = _span(run)
            junctions = _junctions(spec, s, facing)
            fixed, movable = [], []
            for (u, w, kind) in run["openings"]:
                tag = _tag_at(tags, "ext_%d_%s" % (s, facing), facing, u)
                (movable if (s >= 1 and kind == "window" and not tag) else fixed).append((u, w))
            placed = list(fixed)
            if grammar == "over_sym":
                below = [u for (u, _w) in finals.get((s - 1, facing), [])]
                placed += _over_sym(movable, below, fixed, (lo + hi) / 2.0, reach, lo, hi, wt, junctions, res)
                finals[(s, facing)] = placed
                if s >= 1:
                    centre = (lo + hi) / 2.0
                    res["mirrored"][0] += _mirrored([u for (u, _w) in placed], centre)
                    res["mirrored"][1] += len(placed)
                    res["mirrored_built"][0] += _mirrored([o[0] for o in run["openings"]], centre)
                    res["mirrored_built"][1] += len(run["openings"])
                continue
            if grammar == "over":
                targets = [u for (u, _w) in finals.get((s - 1, facing), [])]
            else:
                n = max(1, int(round((hi - lo) / BAY)))
                bw = (hi - lo) / n
                targets = [lo + (i + 0.5) * bw for i in range(n)]
                if grammar == "entrance" and prim is not None:
                    k = min(range(n), key=lambda i: abs(targets[i] - prim))
                    shift = prim - targets[k]
                    targets = [t + shift for t in targets] + [targets[0] + shift - bw, targets[-1] + shift + bw]
                elif grid is not None:
                    fw, anchor, _gu = grid
                    i0 = int((lo - anchor) // fw)
                    targets = [anchor + i * fw for i in range(i0 - 1, int((hi - anchor) // fw) + 2)]
            taken = set()
            for (u, w) in sorted(movable, key=lambda m: m[0]):
                res["movable"] += 1
                # `fit` stacks first: a bay with a ground-floor opening under it before one without, then nearness
                pref = (lambda t: 0 if census._near(t, grid[2]) else 1) if grid is not None else (lambda t: 0)
                cands = [(d, i, t) for (_p, d, i, t) in
                         sorted((pref(t), abs(t - u), i, t) for i, t in enumerate(targets) if i not in taken)]
                if grammar == "over":
                    cands = [c for c in cands if c[0] <= reach + 1e-9]
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
                    if any(min(u, best[1]) < j < max(u, best[1]) for j in junctions):
                        res["rehomed"] += 1
                placed.append((best[1], w))
            finals[(s, facing)] = placed
            if s >= 1:
                centre = (lo + hi) / 2.0
                res["mirrored"][0] += _mirrored([u for (u, _w) in placed], centre)
                res["mirrored"][1] += len(placed)
                res["mirrored_built"][0] += _mirrored([o[0] for o in run["openings"]], centre)
                res["mirrored_built"][1] += len(run["openings"])
    for (s, facing), placed in finals.items():
        below = finals.get((s - 1, facing))
        if not below:
            continue
        key = "ground" if s == 1 else "upper"
        st, n = res["pairs"].get(key, (0, 0))
        res["pairs"][key] = (st + sum(1 for (u, _w) in placed if census._near(u, [b for (b, _bw) in below])),
                             n + len(placed))
    res["finals"] = finals
    return res


def pool(build):
    """The themed pool's multi-storey enterable buildings, with their specs read by Deli Counter."""
    complete, _i, _n = census.bl.index(build)
    fit, _u = census.bl.themed_report(complete)
    specs = os.path.join(os.path.dirname(build.rstrip("/\\")), "specs")
    ids = []
    for e in fit:
        sp = spec_loader.load_spec(os.path.join(specs, e["id"] + ".json"))
        if getattr(sp, "facade", False):
            continue
        b, _r = census.building(e["id"], build)
        if max([max(f["storeys"]) + 1 for f in b["faces"].values()] or [0]) >= 2:
            ids.append((e["id"], sp))
    return ids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", default=os.path.join(census.F, "deli_counter", "build"))
    ap.add_argument("--lf", default=None)
    a = ap.parse_args()
    ids = pool(a.build)
    print("[predict] %d multi-storey enterable buildings in Level Factory's themed pool; BAY %.1f m, MIN_PIER %.1f m"
          % (len(ids), BAY, MIN_PIER))
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
    print("%-9s %7s %6s %8s %-16s %-38s %11s %13s %9s %13s %7s" % (
        "grammar", "movable", "moved", "new room", "refused", "deflected", "move med/max", "stacked g->1", "above",
        "mirrored up", "touched"))
    fit_line = None
    for label, g, reach in ROWS:
        tot = {"movable": 0, "moved": 0, "rehomed": 0, "refused": collections.Counter(),
               "deflected": collections.Counter(), "moves": [], "pairs": {"ground": [0, 0], "upper": [0, 0]},
               "mirrored": [0, 0], "mirrored_built": [0, 0], "fit": [0, 0]}
        touched = 0
        for bid, sp in ids:
            r = predict(bid, a.build, sp, g, reach)
            for k in ("movable", "moved", "rehomed"):
                tot[k] += r[k]
            tot["refused"].update(r["refused"])
            tot["deflected"].update(r["deflected"])
            tot["moves"] += r["moves"]
            for key, (st, n) in r["pairs"].items():
                tot["pairs"][key][0] += st
                tot["pairs"][key][1] += n
            for k in ("mirrored", "mirrored_built"):
                tot[k][0] += r[k][0]
                tot[k][1] += r[k][1]
            tot["fit"][0] += r["fit_aligned"]
            tot["fit"][1] += r["fit_ground"]
            touched += 1 if r["moved"] else 0
        mv = tot["moves"]
        print("%-9s %7d %6d %8d %-16s %-38s %5s/%-5s %6d of %-4d %3d of %-3d %5d of %-4d %5d" % (
            label, tot["movable"], tot["moved"], tot["rehomed"],
            ", ".join("%s %d" % kv for kv in sorted(tot["refused"].items())) or "-",
            ", ".join("%s %d" % kv for kv in sorted(tot["deflected"].items())) or "-",
            "%.2f" % statistics.median(mv) if mv else "-", "%.2f" % max(mv) if mv else "-",
            tot["pairs"]["ground"][0], tot["pairs"]["ground"][1], tot["pairs"]["upper"][0], tot["pairs"]["upper"][1],
            tot["mirrored"][0], tot["mirrored"][1], touched))
        built_mirror = tot["mirrored_built"]
        if g == "fit":
            fit_line = tot["fit"]
    print()
    print("as built, mirrored up: %d of %d upper-storey openings have a partner mirrored about their face's centre"
          % (built_mirror[0], built_mirror[1]))
    print("fit: ground-floor openings standing on the best grid their own face admits, once a face: %d of %d"
          % (fit_line[0], fit_line[1]))
    print()
    print("movable: upper-storey windows with no gameplay tag; moved: those the grammar moved (a window already on its")
    print("target is not a move); new room: moves across a partition's junction with the wall, into another room;")
    print("refused: no target left, the window where it is; deflected: windows whose first target was turned down,")
    print("by why, that took another; move: metres along the face; stacked: openings over an opening on the storey")
    print("below, after; mirrored up: upper-storey openings with a partner mirrored about the face's centre, after;")
    print("touched: buildings with at least one window moved, each of which would need a refurnish and a rebuild.")


if __name__ == "__main__":
    main()
