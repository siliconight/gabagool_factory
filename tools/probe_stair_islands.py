r"""Why a stair's two ends land on disjoint navmesh islands.

    python probe_stair_islands.py                  (deli_counter/build)
    python probe_stair_islands.py <build_dir>
    python probe_stair_islands.py <build_dir> --all      every stair, not just failures
    python probe_stair_islands.py <build_dir> --json

Run from the FACTORY ROOT or from inside `deli_counter`. Read-only, and it
needs neither Blender nor Godot: it reads the `.navgate.json` verdicts the
gate already wrote, the `.gameplay.json` manifests, and the `.glb` geometry
(JSON chunk only -- no binary decode, no mesh library).

THE FAILURE IT EXPLAINS. `check.py` runs `nav_gate.py --all`, and on
2026-08-13 that reported:

    nav-gate: 7/135 shell(s) FAILED traversal

Every one of the eight failing stairs failed the same way -- `no_path
(endpoints on disjoint islands)`. The navmesh exists at the bottom of the
stair and at the top, and somewhere in between it stops.

WHAT WAS RULED OUT, BY MEASUREMENT, BEFORE LANDING ON THE TWO BELOW:

  stale geometry   all 138 shells were rebuilt in one pass and the freshness
                   gate passes. The 2026-08-05 note blamed exactly this
                   symptom on fossils; with freshness now guaranteed, the same
                   shells still fail. That diagnosis did not survive.
  facade lights    the most recent commit before the failing check. Zero
                   nodes matching light/lamp/sconce/sign/fixture in any
                   failing shell's GLB.
  clear width      2.2 m fails, 1.6 m both fails and passes.
  pitch            the shallowest stair in the set (31 deg) fails and the
                   steepest (45 deg) passes; none exceed the bake's 55.
  riser height     every stair has ~0.2 m risers, including the ones that pass.
  tread depth      0.222 m fails while 0.238 and 0.267 pass. Correlated, not
                   causal.

WHAT SURVIVED. Two variables, between them accounting for every stair
measured:

  1. INTERMEDIATE LANDINGS. Every stair with more than one landing fails;
     every stair with exactly one (the top) passes. 7 of the 8 failures.
     The strongest evidence is inside one shell: cbp_town_finale's stair_2
     and stair_3 have one landing each and pass, while stair_0 and stair_1 in
     the same file, same build, same bake have three and fail.

  2. CLEAR WIDTH AGAINST AGENT RADIUS, for the one stair the first does not
     explain. night_pawn_stair_0 has a single landing and still fails. It is
     also the only stair in the set at `clear_width_m: 1.0` with
     `max_agents_abreast: 1`. The bake erodes 0.40 m from each edge, which
     leaves 0.2 m of walkable strip, and its navmesh breaks mid-flight rather
     than at a landing -- a different location for a different reason.

Both are stated as measured correlations over the stairs this can see. The
column that settles them is `navmesh gap`: where the navmesh actually stops.
If the gap brackets a landing height, read 1; if it sits mid-flight, read 2.

`none` NEXT TO A FAILURE IS NOT A CONTRADICTION. The break has two shapes and
only one of them is a band. cbp_town_finale's two failing stairs have islands
covering their whole rise and still no path, because the two flights of the
switchback are SEPARATE islands at the same heights that never join across
the half-landing. Vertical band and lateral split are the same defect seen
from two directions, which is why the landing count predicts both.

A NOTE ON MAPPING STAIRS TO GEOMETRY. The GLB names step nodes `stairK_*`
while the manifest names stairs `a03_stair_main`, `main_stack`,
`night_deli_stair_0` -- three conventions, none of them K. Parsing K out of
the id silently mislabelled two passing bank_branch_a04 stairs as failures on
the first run of this analysis. The mapping used here is POSITIONAL, with the
name-suffix used only to confirm it, and `--all` prints the pairing so it can
be audited rather than trusted.
"""
from __future__ import annotations

import glob
import json
import math
import os
import re
import struct
import sys
from statistics import median

# ------------------------------------------------------------------ glb ----

def glb_json(path: str) -> dict:
    """The JSON chunk of a .glb. Node names, transforms and accessor bounds
    all live here, so nothing below needs the binary chunk decoded."""
    with open(path, "rb") as f:
        data = f.read()
    magic, _ver, total = struct.unpack_from("<III", data, 0)
    if magic != 0x46546C67:
        raise ValueError(f"{path} is not a glb")
    off = 12
    while off < total:
        clen, ctype = struct.unpack_from("<II", data, off)
        off += 8
        chunk = data[off:off + clen]
        off += clen
        if ctype == 0x4E4F534A:
            return json.loads(chunk.decode("utf-8"))
    raise ValueError(f"{path} has no JSON chunk")


def _mul(a, b):
    return [sum(a[r * 4 + k] * b[k * 4 + c] for k in range(4))
            for r in range(4) for c in range(4)]


def _trs(n):
    if "matrix" in n:                                   # glTF is column-major
        m = n["matrix"]
        return [m[0], m[4], m[8], m[12], m[1], m[5], m[9], m[13],
                m[2], m[6], m[10], m[14], m[3], m[7], m[11], m[15]]
    t = n.get("translation", [0, 0, 0])
    s = n.get("scale", [1, 1, 1])
    x, y, z, w = n.get("rotation", [0, 0, 0, 1])
    r = [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w),
         2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w),
         2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]
    return [r[0] * s[0], r[1] * s[1], r[2] * s[2], t[0],
            r[3] * s[0], r[4] * s[1], r[5] * s[2], t[1],
            r[6] * s[0], r[7] * s[1], r[8] * s[2], t[2],
            0, 0, 0, 1]


def node_world(g: dict) -> dict:
    """{node_index: (name, world_matrix, mesh_index)} with parents applied."""
    nodes = g.get("nodes", [])
    out = {}
    ident = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]

    def walk(i, parent):
        n = nodes[i]
        m = _mul(parent, _trs(n))
        out[i] = (n.get("name", f"node{i}"), m, n.get("mesh"))
        for c in n.get("children", []):
            walk(c, m)

    roots = set(range(len(nodes)))
    for n in nodes:
        for c in n.get("children", []):
            roots.discard(c)
    for r in sorted(roots):
        walk(r, ident)
    return out


def mesh_bounds(g: dict, mi: int):
    lo = [math.inf] * 3
    hi = [-math.inf] * 3
    for prim in g["meshes"][mi].get("primitives", []):
        a = prim.get("attributes", {}).get("POSITION")
        if a is None:
            continue
        acc = g["accessors"][a]
        if "min" not in acc or "max" not in acc:
            continue
        for k in range(3):
            lo[k] = min(lo[k], acc["min"][k])
            hi[k] = max(hi[k], acc["max"][k])
    return None if lo[0] == math.inf else (lo, hi)


def _pt(m, p):
    return (m[0] * p[0] + m[1] * p[1] + m[2] * p[2] + m[3],
            m[4] * p[0] + m[5] * p[1] + m[6] * p[2] + m[7],
            m[8] * p[0] + m[9] * p[1] + m[10] * p[2] + m[11])


# ---------------------------------------------------------------- steps ----

#: Geometry that is ALWAYS inside a stair's own volume and is not an
#: obstruction: the floor slabs it passes through, and the stair's own ramp
#: and landing colliders. Everything else in there is something placed in a
#: stairwell. Measured, not assumed: every stair that passes has only these.
_STRUCTURAL = re.compile(r"^(slab|stair\d*(ramp|col)|.*-colonly$)", re.I)


def intruders(path: str, prism) -> list:
    """Non-structural meshes whose bounds overlap the stair's volume.

    THE POINT. `office_stair_0` and `lf_lot_demo_001_5118_stair_0` are the
    same stair -- switchback, 1.6 m clear, 0.222 m going, 42 deg, two
    landings -- and one fails while the other passes. Nothing measured ON the
    stair separates them. What is IN the stair does: the failing one has an
    `elevator_block` in the stairwell and the passing one has nothing but
    slabs. `night_deli`'s list includes a mesh named `crate_stack_stairwell`.
    """
    g = glb_json(path)
    out = []
    for _i, (name, m, mi) in node_world(g).items():
        if mi is None or re.match(r"stair\d+_", name) or _STRUCTURAL.match(name):
            continue
        b = mesh_bounds(g, mi)
        if not b:
            continue
        lo, hi = b
        cs = [_pt(m, (x, y, z)) for x in (lo[0], hi[0])
              for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
        xs = [c[0] for c in cs]
        ys = [c[1] for c in cs]
        zs = [c[2] for c in cs]
        if (max(xs) < prism[0] or min(xs) > prism[1]
                or max(ys) < prism[2] or min(ys) > prism[3]
                or max(zs) < prism[4] or min(zs) > prism[5]):
            continue
        out.append(name)
    return sorted(set(out))


def step_groups(path: str) -> dict:
    """{K: [step, ...]} for nodes named `stairK_*`, in world space."""
    g = glb_json(path)
    nw = node_world(g)
    groups: dict[int, list] = {}
    for _i, (name, m, mi) in nw.items():
        mt = re.match(r"stair(\d+)_", name)
        if mi is None or not mt:
            continue
        b = mesh_bounds(g, mi)
        if not b:
            continue
        lo, hi = b
        cs = [_pt(m, (x, y, z)) for x in (lo[0], hi[0])
              for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
        xs = [c[0] for c in cs]
        ys = [c[1] for c in cs]
        zs = [c[2] for c in cs]
        groups.setdefault(int(mt.group(1)), []).append(
            {"top": max(ys), "cx": (min(xs) + max(xs)) / 2,
             "cz": (min(zs) + max(zs)) / 2,
             "w": max(xs) - min(xs), "d": max(zs) - min(zs),
             "box": (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))})
    return groups


def prism(steps: list):
    bs = [s["box"] for s in steps]
    return (min(b[0] for b in bs), max(b[1] for b in bs),
            min(b[2] for b in bs), max(b[3] for b in bs),
            min(b[4] for b in bs), max(b[5] for b in bs))


def describe(steps: list) -> dict:
    """Going, riser and landing heights, read off the steps themselves.

    A LANDING is a horizontal hop much larger than the typical going -- the
    walk turns or flattens. Derived from the geometry rather than the
    manifest, because the manifest's `landings` lists only the two ends and
    the ones in the middle are exactly what this is looking for.
    """
    steps = sorted(steps, key=lambda s: s["top"])
    hops = []
    for a, b in zip(steps, steps[1:]):
        dy = b["top"] - a["top"]
        if dy <= 0.001:
            continue
        hops.append((math.hypot(b["cx"] - a["cx"], b["cz"] - a["cz"]), dy,
                     a["top"]))
    if not hops:
        return {"steps": len(steps)}
    going = median(h[0] for h in hops)
    riser = median(h[1] for h in hops)
    land = [round(t, 2) for dh, _dy, t in hops if dh > going * 1.8]
    pitch = median(math.degrees(math.atan2(dy, dh))
                   for dh, dy, _t in hops if dh > 0.001)
    return {"steps": len(steps), "going": round(going, 3),
            "riser": round(riser, 3), "pitch": round(pitch, 1),
            "width": round(median(max(s["w"], s["d"]) for s in steps), 2),
            "landings": land, "n_landings": len(land),
            "y_lo": round(min(s["top"] for s in steps), 2),
            "y_hi": round(max(s["top"] for s in steps), 2)}


#: The navmesh sits this far above the surface it was baked from, so the band
#: between a stair's first step and the lowest island is an artefact of the
#: bake and not a break in it. NOT assumed -- measured: every stair that
#: PASSES shows the same 0.19->0.3 or 0.2->0.3 band at its foot. A gap
#: starting at the stair's own bottom and no taller than this is dropped,
#: which is what stops the probe reporting the offset as the defect.
_BAKE_OFFSET = 0.35


def navmesh_gaps(islands: list, y_lo: float, y_hi: float) -> list:
    """Every band between y_lo and y_hi that no island covers, tallest first.

    This is the whole question stated as a number: the stair runs from y_lo to
    y_hi, the islands cover parts of it, and what is left is where the walk
    stops.
    """
    spans = sorted((i["y_min"], i["y_max"]) for i in islands
                   if i["y_max"] >= y_lo and i["y_min"] <= y_hi)
    if not spans:
        return [(round(y_lo, 2), round(y_hi, 2))]
    gaps = []
    cursor = y_lo
    for lo, hi in spans:
        if lo > cursor:
            gaps.append((cursor, lo))
        cursor = max(cursor, hi)
    if cursor < y_hi:
        gaps.append((cursor, y_hi))
    gaps = [g for g in gaps
            if not (abs(g[0] - y_lo) < 0.01 and g[1] - g[0] <= _BAKE_OFFSET)]
    gaps.sort(key=lambda g: g[0] - g[1])
    return [(round(a, 2), round(b, 2)) for a, b in gaps]


def pair_stairs(manifest_stairs: list, verdict_stairs: list, groups: dict):
    """Map step-node group K to a stair id. POSITIONAL, name only confirms.

    Three id conventions are in play (`a03_stair_main`, `main_stack`,
    `night_deli_stair_0`) and none of them is K. Parsing K out of the id
    mislabelled two passing stairs as failures the first time this analysis
    was run, so the order is used and the name is reported beside it for a
    human to check.
    """
    ids = [s.get("id") for s in (manifest_stairs or [])]
    status = {s.get("id"): s.get("status") for s in (verdict_stairs or [])}
    ks = sorted(groups)
    pairs = []
    for pos, k in enumerate(ks):
        sid = ids[pos] if pos < len(ids) else None
        suffix = None
        if sid:
            mt = re.search(r"(\d+)$", sid)
            suffix = int(mt.group(1)) if mt else None
        pairs.append({"group": k, "stair_id": sid,
                      "status": status.get(sid, "?"),
                      "suffix_agrees": (suffix is None or suffix == k),
                      "manifest": (manifest_stairs or [])[pos]
                      if pos < len(manifest_stairs or []) else {}})
    if len(ks) != len(ids):
        for p in pairs:
            p["suffix_agrees"] = False
    return pairs


def collect(build: str) -> list:
    rows = []
    for glb in sorted(glob.glob(os.path.join(build, "*.glb"))):
        stem = glb[:-4]
        ngp, gpp = stem + ".navgate.json", stem + ".gameplay.json"
        if not (os.path.exists(ngp) and os.path.exists(gpp)):
            continue
        try:
            ng = json.load(open(ngp, encoding="utf-8"))
            gp = json.load(open(gpp, encoding="utf-8"))
            groups = step_groups(glb)
        except (OSError, ValueError):
            continue
        pairs = pair_stairs(gp.get("stair_systems") or [],
                            ng.get("stairs") or [], groups)
        for p in pairs:
            d = describe(groups[p["group"]])
            if "going" not in d:
                continue
            man = p["manifest"]
            intr = intruders(glb, prism(groups[p["group"]]))
            rows.append({
                "shell": os.path.basename(stem), "stair_id": p["stair_id"],
                "group": p["group"], "status": p["status"],
                "suffix_agrees": p["suffix_agrees"],
                "shape": man.get("shape"),
                "clear_width_m": man.get("clear_width_m"),
                "floors_served": man.get("floors_served"),
                "gaps": navmesh_gaps(ng.get("islands") or [],
                                     d["y_lo"], d["y_hi"]),
                "intruders": intr, "n_intruders": len(intr),
                **d})
    return rows


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    build = args[0] if args else (
        "build" if os.path.isdir("build") else os.path.join("deli_counter",
                                                            "build"))
    if not os.path.isdir(build):
        raise SystemExit(f"no build directory at {build}")
    print(f"reading {build}\n")
    rows = collect(build)
    if not rows:
        raise SystemExit("no shell had all three of .glb, .navgate.json and "
                         ".gameplay.json -- run nav_gate.py --all first")
    if "--json" in argv:
        print(json.dumps(rows, indent=2, sort_keys=True))
        return 0

    bad = [r for r in rows if r["status"] != "ok"]
    show = rows if "--all" in argv else bad
    print(f"{len(rows)} stair(s) across {len({r['shell'] for r in rows})} "
          f"shell(s); {len(bad)} not traversable\n")

    hdr = (f"{'':<4} {'shell':<34} {'stair':<24} {'cw':>4} {'going':>6} "
           f"{'lands':>5} {'in':>3}  in the stair volume / navmesh gap")
    print(hdr)
    print("-" * len(hdr))
    for r in sorted(show, key=lambda r: (r["status"] == "ok", r["shell"])):
        g0 = r["gaps"][0] if r["gaps"] else None
        gap = "none" if g0 is None else f"{g0[0]} -> {g0[1]}"
        at = ""
        if g0 and r["landings"]:
            near = [y for y in r["landings"] if g0[0] - 0.5 <= y <= g0[1] + 0.5]
            at = "  (brackets a landing)" if near else "  (mid-flight)"
        elif g0:
            at = "  (mid-flight)"
        if g0 is None and r["status"] != "ok":
            # NO vertical band missing, and still no path. The break is
            # LATERAL: the two flights of the switchback are separate islands
            # covering the same heights, never joined across the half-landing.
            # Same defect as the banded ones, seen end-on.
            at = "  (lateral: islands share the height, never join)"
        if g0 and len(r["gaps"]) > 1:
            at += f"  +{len(r['gaps']) - 1} more"
        what = ", ".join(r["intruders"][:3]) or gap + at
        if r["intruders"] and len(r["intruders"]) > 3:
            what += f", +{len(r['intruders']) - 3}"
        print(f"{('FAIL' if r['status'] != 'ok' else 'ok'):<4} "
              f"{r['shell'][:34]:<34} {str(r['stair_id'])[:24]:<24} "
              f"{str(r['clear_width_m']):>4} {r['going']:>6} "
              f"{r['n_landings']:>5} {r['n_intruders']:>3}  {what[:58]}")

    unsure = [r for r in rows if not r["suffix_agrees"]]
    if unsure:
        print(f"\n  {len(unsure)} stair(s) whose id does not end in their step "
              f"group's number.\n  The pairing there is POSITIONAL -- check it "
              f"with --all before quoting a verdict:")
        for r in unsure[:8]:
            print(f"    {r['shell']}: group stair{r['group']} <- "
                  f"{r['stair_id']}  ({r['status']})")

    if bad:
        ok_rows = [r for r in rows if r["status"] == "ok"]
        # THE TEST THIS PROBE EXISTS TO SURVIVE. An earlier reading of ten
        # shells said every failure had more than one landing and no passing
        # stair did. Across all of them, fifteen passing stairs have more than
        # one landing -- the rule died the moment it met the full set. So the
        # numbers below are printed for BOTH sides every run: a rule that only
        # counts the failures is not a rule, it is a description.
        fb = sum(1 for r in bad if r["n_intruders"])
        fo = sum(1 for r in ok_rows if r["n_intruders"])
        print(f"\n  something in the stair volume: {fb}/{len(bad)} failures, "
              f"{fo}/{len(ok_rows)} passing stairs")
        lb = sum(1 for r in bad if r["n_landings"] > 1)
        lo = sum(1 for r in ok_rows if r["n_landings"] > 1)
        print(f"  more than one landing:         {lb}/{len(bad)} failures, "
              f"{lo}/{len(ok_rows)} passing stairs")
        if fo:
            print(f"\n  {fo} passing stair(s) also have something in the "
                  f"volume, so intrusion alone does not\n  decide it -- WHERE "
                  f"the thing sits must matter. Worth listing:")
            for r in ok_rows[:6]:
                if r["n_intruders"]:
                    print(f"    ok  {r['shell']} {r['stair_id']}: "
                          f"{', '.join(r['intruders'][:4])}")
        clean = [r for r in bad if not r["n_intruders"]]
        for r in clean:
            print(f"\n  NOT explained by intrusion: {r['shell']} "
                  f"{r['stair_id']} -- nothing but structure in its volume")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
