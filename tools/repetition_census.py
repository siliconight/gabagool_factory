#!/usr/bin/env python3
"""Measure how repetitive a composed building actually is.

WHY THIS EXISTS. Every other claim in this factory is measured -- the light
census, the span probe, the nav gate, the cold-run journal. "Does this facade
read as machine-made" was not, so it got answered by walking the level and
squinting, and a value tuned that way cannot be reproduced across themes or
defended against the next person's eye. Walked 2026-08-29: `bank_block_001`
seed 7003 read as Lego, and nobody could say by how much.

WHAT IT MEASURES, and what it deliberately does not. It reads the COMPOSED
scene -- the `.tscn` that actually ships -- and counts what is instanced where.
It reports numbers. It does not decide whether a building is too repetitive,
because the threshold is a taste call and this tool has no taste; and it does
not attribute repetition to a cause, because the same number can come from a
small kit, a coarse module size, or a resolver that collapses variants, and one
reading cannot tell them apart. Pick the gate from the numbers, not from here.

THE ONE NUMBER, if you only read one: `longest_identical_run` per wall run.
Its floor is 1 (no module ever appears twice in a row) and its ceiling is the
run's own segment count (the whole wall is one module repeated). That is the
Lego measurement, in the units a player experiences it.

WHAT THIS RULER CANNOT SEE, stated up front so it is not discovered later by
being surprised. It measures the repetition of the FORM VOCABULARY -- which
mesh, at which size, how many times, how many in a row. It is therefore the
right instrument for kit work (more wall widths, wallCorner, per-module
selection) and the WRONG instrument for per-instance variation. Patina's
`--slot-variation` and Pixelcoat's gen-7 `variations` change how two copies of
one mesh LOOK without changing that they are one mesh, so a run of fourteen
would still read fourteen here after they landed. Do not read a flat number as
that work having failed; read it as this ruler not being pointed at it. Judging
per-instance variation needs a second instrument that reads appearance, and
none exists yet.

FORM, NOT STEM. Two instances count as the same thing only when they share a
stem AND a scale. Deli Counter scales `wallEnd` per slot -- one unit box fills
every remainder -- so a run of three wallEnds at 1.7, 0.3 and 0.3 metres wide
is two forms, not one, and calling it one would flatter the building.

Usage:
    python tools/repetition_census.py <building.tscn> [more.tscn ...]
    python tools/repetition_census.py <scene.tscn> --json out.json
    python tools/repetition_census.py <scene.tscn> --baseline before.json
    python tools/repetition_census.py --selftest
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import os
import re
import sys

_EXT = re.compile(
    r'^\[ext_resource\s+type="PackedScene"\s+path="([^"]+)"\s+id="([^"]+)"\]')
_NODE = re.compile(
    r'^\[node\s+name="([^"]+)".*?instance=ExtResource\("([^"]+)"\)')
_XFORM = re.compile(r'^transform\s*=\s*Transform3D\(([^)]*)\)')

#: `ext_0_N_seg3` / `int_-1_2_open0` -> run id `ext_0_N` / `int_-1_2`.
#: Deli Counter emits one wall RUN per building face per storey and indexes
#: along it, so the node name already carries the grouping this tool needs --
#: no slots file, no manifest, no second source to fall out of sync with.
_RUN = re.compile(r'^((?:ext|int)_-?\d+_(?:[NSEW]|\d+))_(?:seg|open)\d+')


def stem_of(path):
    """`res://art/zoo/wall_delco_01_w200.glb` -> `wall_delco_01_w200`."""
    return os.path.splitext(os.path.basename(path))[0]


def parse_scene(text):
    """Instanced nodes, in file order: (name, stem, scale, origin).

    Nodes with no `transform` line carry the identity -- Godot omits it -- so
    they get scale (1,1,1) at the origin rather than being dropped.
    """
    ids, out = {}, []
    pending = None
    for line in text.splitlines():
        m = _EXT.match(line)
        if m:
            ids[m.group(2)] = stem_of(m.group(1))
            continue
        m = _NODE.match(line)
        if m:
            if pending:
                out.append(pending)
            pending = [m.group(1), ids.get(m.group(2), "?"),
                       (1.0, 1.0, 1.0), (0.0, 0.0, 0.0)]
            continue
        if pending is not None:
            m = _XFORM.match(line)
            if m:
                try:
                    f = [float(v) for v in m.group(1).split(",")]
                except ValueError:
                    f = []
                if len(f) == 12:
                    pending[2] = tuple(
                        round(math.sqrt(f[i] ** 2 + f[i + 1] ** 2 + f[i + 2] ** 2), 4)
                        for i in (0, 3, 6))
                    pending[3] = (f[9], f[10], f[11])
            elif line.startswith("["):
                out.append(pending)
                pending = None
    if pending:
        out.append(pending)
    return [tuple(n) for n in out]


#: Roles Deli Counter tiles along a wall run. Plates (floor/ceiling/roof) and
#: props are excluded: a floor is one slot per room and repeating it is not a
#: defect, so counting it would dilute the only number this tool is for.
_RUN_ROLES = ("wall", "doorway", "window", "breach", "vault_door",
              "teller_line", "safe_deposit_boxes")


def parse_slots(doc):
    """Deli Counter's own `*.slots.json` -> the same tuples `parse_scene` makes.

    WHY BOTH READERS. The `.tscn` is what ships and is the honest thing to
    measure, but it only exists after a themed compose, and most of the
    library on disk never got one. The slot manifest is written by every
    `deli_generate` there has ever been, carries its run id in `wall` rather
    than in a node name, and decides the same vocabulary one step earlier --
    so it reads the whole back catalogue.

    THE TWO READERS HAVE NOT BEEN CROSS-CHECKED ON ONE BUILDING, and until
    they are, a slots reading and a scene reading are two measurements and not
    one. The check needs a building with both, which means a `shell.slots.json`
    out of a workspace that also composed -- and level_factory hardlinks its
    job outputs, so pulling one off the machine needs a copy made first. Until
    that is done, compare slots to slots and scenes to scenes.

    The stand-in stem is `<role>_<style>_<size_mod>`, and the stand-in scale
    is `fit.dims`. That is exactly the tuple `themed_tscn.resolve_themed_stem`
    turns into a filename plus the scale DC applies to it, so two slots that
    tie here are two slots that WILL resolve to one mesh at one size.
    """
    out = []
    for sl in doc.get("slots", []):
        if sl.get("role") not in _RUN_ROLES or not sl.get("wall"):
            continue
        dims = (sl.get("fit") or {}).get("dims") or [0, 0, 0]
        tr = (sl.get("transform") or {}).get("translation") or [0, 0, 0]
        stem = "%s_%02d_%s" % (sl.get("role"), int(sl.get("style") or 1),
                               sl.get("size_mod") or "full")
        mat = sl.get("material")
        if mat:
            stem += "_" + str(mat)
        # The slot_id IS `<run>_seg<k>` / `<run>_open<j>`, the same shape the
        # composer writes as a node name, so one run regex serves both readers.
        out.append((sl.get("slot_id") or sl["wall"], stem,
                    tuple(round(float(v), 4) for v in dims[:3]),
                    tuple(float(v) for v in tr[:3])))
    return out


def form(stem, scale):
    """What the eye compares: the mesh AND the scale it was stretched to."""
    return "%s@%.2fx%.2fx%.2f" % (stem, scale[0], scale[1], scale[2])


def _axis(origins):
    """Which world axis the run travels along -- whichever spreads furthest."""
    if not origins:
        return 0
    spread = [max(o[i] for o in origins) - min(o[i] for o in origins)
              for i in (0, 1, 2)]
    return spread.index(max(spread))


def run_report(name, members):
    """One wall run's numbers. `members` is [(node, stem, scale, origin)]."""
    origins = [m[3] for m in members]
    ax = _axis(origins)
    # SPATIAL ORDER, not emission order. `_seg<k>` counts up along the run,
    # but openings are emitted in their own pass and interleave with it, so
    # reading the file order would report a sequence the wall does not have.
    ordered = sorted(members, key=lambda m: m[3][ax])
    forms = [form(m[1], m[2]) for m in ordered]

    longest, cur = 1, 1
    for a, b in zip(forms, forms[1:]):
        cur = cur + 1 if a == b else 1
        longest = max(longest, cur)
    counts = collections.Counter(forms)
    top, top_n = counts.most_common(1)[0]

    pos = [m[3][ax] for m in ordered]
    gaps = [round(b - a, 3) for a, b in zip(pos, pos[1:])]
    pitch, on_pitch = None, 0.0
    if gaps:
        pitch, hits = collections.Counter(gaps).most_common(1)[0]
        on_pitch = hits / float(len(gaps))
    return {
        "run": name,
        "segments": len(ordered),
        "span_m": round(max(pos) - min(pos), 3) if pos else 0.0,
        "distinct_stems": len({m[1] for m in ordered}),
        "distinct_forms": len(counts),
        "longest_identical_run": longest,
        "dominant_form": top,
        "dominant_share": round(top_n / float(len(ordered)), 3),
        "pitch_m": pitch,
        "on_pitch_share": round(on_pitch, 3),
        "sequence": forms,
    }


def census(path):
    """One building's reading, from either source.

    `.tscn` -> the composed scene that ships. `.json` -> Deli Counter's slot
    manifest, one step upstream. Both produce the same tuples, so everything
    below this line is shared and the two readings are comparable by
    construction rather than by care.
    """
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    if path.endswith(".json"):
        nodes, source = parse_slots(json.loads(raw)), "slots"
    else:
        nodes, source = parse_scene(raw), "scene"

    runs, loose = collections.OrderedDict(), []
    for n in nodes:
        m = _RUN.match(n[0])
        if m:
            runs.setdefault(m.group(1), []).append(n)
        else:
            loose.append(n)

    reports = [run_report(k, v) for k, v in runs.items() if v]
    reports.sort(key=lambda r: (-r["longest_identical_run"], -r["segments"]))

    inst = sum(r["segments"] for r in reports)
    forms = collections.Counter()
    for v in runs.values():
        for n in v:
            forms[form(n[1], n[2])] += 1
    return {
        "scene": os.path.basename(path),
        "source": source,
        "wall_instances": inst,
        "loose_nodes": len(loose),
        "distinct_stems": len({n[1] for v in runs.values() for n in v}),
        "distinct_forms": len(forms),
        # How many times the average form is reused. 1.0 = every module in the
        # building is unique; 20.0 = twenty placements per distinct thing.
        "reuse_factor": round(inst / float(len(forms)), 2) if forms else 0.0,
        "worst_run": reports[0]["longest_identical_run"] if reports else 0,
        "top_forms": forms.most_common(8),
        "runs": reports,
    }


def render(c, baseline=None):
    b = {r["run"]: r for r in baseline["runs"]} if baseline else {}
    out = []
    out.append("%s -- %d wall instances, %d distinct stems, %d distinct forms"
               % (c["scene"], c["wall_instances"], c["distinct_stems"],
                  c["distinct_forms"]))
    out.append("  reuse factor %.2f placements per form   "
               "worst run %d identical in a row"
               % (c["reuse_factor"], c["worst_run"]))
    if baseline:
        out.append("  baseline %s: reuse %.2f, worst run %d"
                   % (baseline["scene"], baseline["reuse_factor"],
                      baseline["worst_run"]))
    out.append("")
    out.append("  %-12s %4s %8s %6s %6s %9s %7s  %s"
               % ("run", "segs", "span_m", "stems", "forms", "longest",
                  "pitch", "dominant form (share)"))
    for r in c["runs"]:
        delta = ""
        if r["run"] in b:
            d = r["longest_identical_run"] - b[r["run"]]["longest_identical_run"]
            delta = "  (%+d)" % d if d else "  (=)"
        out.append("  %-12s %4d %8.2f %6d %6d %9d %7s  %s (%.0f%%)%s"
                   % (r["run"], r["segments"], r["span_m"],
                      r["distinct_stems"], r["distinct_forms"],
                      r["longest_identical_run"],
                      "-" if r["pitch_m"] is None else "%.2f" % r["pitch_m"],
                      r["dominant_form"], 100 * r["dominant_share"], delta))
    out.append("")
    out.append("  most-placed forms:")
    for name, n in c["top_forms"]:
        out.append("    %4d x  %s" % (n, name))
    out.append("")
    out.append("  longest_identical_run floor is 1 (never twice in a row); its")
    out.append("  ceiling is the run's own segment count. No threshold is")
    out.append("  applied here -- that is a taste call, and this is a ruler.")
    return "\n".join(out)


_SELFTEST = '''[gd_scene load_steps=3 format=3]

[ext_resource type="PackedScene" path="res://art/zoo/wall_x_01_w200.glb" id="1_w"]
[ext_resource type="PackedScene" path="res://art/zoo/wallEnd_x_01.glb" id="2_e"]

[node name="site" type="Node3D"]

[node name="ext_0_N_seg0" parent="." instance=ExtResource("1_w")]
transform = Transform3D(1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0)

[node name="ext_0_N_seg1" parent="." instance=ExtResource("1_w")]
transform = Transform3D(1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 2.0, 0.0, 0.0)

[node name="ext_0_N_seg2" parent="." instance=ExtResource("1_w")]
transform = Transform3D(1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 4.0, 0.0, 0.0)

[node name="ext_0_N_seg3" parent="." instance=ExtResource("2_e")]
transform = Transform3D(1.7, 0.0, 0.0, 0.0, 3.3, 0.0, 0.0, 0.0, 0.3, 6.0, 0.0, 0.0)

[node name="ext_0_N_seg4" parent="." instance=ExtResource("2_e")]
transform = Transform3D(0.3, 0.0, 0.0, 0.0, 3.3, 0.0, 0.0, 0.0, 0.3, 7.0, 0.0, 0.0)
'''


def selftest():
    nodes = parse_scene(_SELFTEST)
    assert len(nodes) == 5, nodes
    assert nodes[0][1] == "wall_x_01_w200"
    assert nodes[3][2] == (1.7, 3.3, 0.3), nodes[3]
    r = run_report("ext_0_N", nodes)
    assert r["segments"] == 5
    # three identical w200 in a row, then two wallEnds at DIFFERENT scales --
    # which is the whole point of keying on form and not on stem.
    assert r["longest_identical_run"] == 3, r
    assert r["distinct_stems"] == 2 and r["distinct_forms"] == 3, r
    assert r["pitch_m"] == 2.0 and r["on_pitch_share"] == 0.75, r
    assert r["span_m"] == 7.0, r
    # A run whose modules alternate must floor at 1, not inherit the last max.
    alt = [("a_seg0", "A", (1, 1, 1), (0, 0, 0)),
           ("a_seg1", "B", (1, 1, 1), (1, 0, 0)),
           ("a_seg2", "A", (1, 1, 1), (2, 0, 0))]
    assert run_report("a", alt)["longest_identical_run"] == 1
    print("selftest OK")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("scenes", nargs="*", help="composed .tscn file(s)")
    ap.add_argument("--json", help="write the full reading here")
    ap.add_argument("--baseline", help="a prior --json reading, to diff against")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.scenes:
        ap.error("give me a composed .tscn (or --selftest)")

    base = None
    if args.baseline:
        with open(args.baseline, encoding="utf-8") as fh:
            base = json.load(fh)
    results = []
    for s in args.scenes:
        if not os.path.exists(s):
            sys.stderr.write("no such scene: %s\n" % s)
            return 2
        c = census(s)
        results.append(c)
        print(render(c, base if base and len(args.scenes) == 1 else None))
        print()
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(results[0] if len(results) == 1 else results, fh, indent=1)
        print("wrote %s" % args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
