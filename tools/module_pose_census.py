"""Is every placed module standing the way its slot says? Read off the engine.

Walking cold run 9005's package on 2026-09-11 showed wall panels spun in
their own plane -- 3.3 m long, 2 m tall, floating at mid-height -- and
panels standing across a corridor instead of along it. This measures that
class: every MeshInstance3D under a slot-named node, its world AABB, and for
wall-type slots whether the vertical extent is the storey (standing) or the
module's width (spun), and whether its bottom sits on a floor.

    python tools\\module_pose_census.py <export_project> [--scene mission.tscn]
        [--slots <shell.slots.json>]

With `--slots`, each wall row is judged against its own slot: expected height
dims[2], expected horizontal extents {dims[0], dims[1]} (module-local, so the
rotation does not matter to the set). Prints what it measured and stops.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from godot_probe import ProbeFailed, require_godot, run_probe   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PAYLOAD = os.path.join(HERE, "module_pose_census.gd")
MARK_BEGIN = "<<<MODULE_POSE_JSON"
MARK_END = "MODULE_POSE_JSON>>>"


def census(project_dir, scene="mission.tscn", godot=None, settle=5,
           timeout=600, verbose=False):
    payload, _out, _mirror = run_probe(
        project_dir=project_dir, script_src=PAYLOAD,
        autoload_name="ModulePoseCensus", scene="res://" + scene,
        begin=MARK_BEGIN, end=MARK_END, godot=godot or require_godot(),
        settings={"module_pose": {"settle_frames": settle}},
        headless=True, timeout=timeout, verbose=verbose)
    return payload


def judge(rows, slots_by_id, tol=0.12):
    """Per wall-type row: standing / spun / tipped, and floating or not."""
    out = []
    for r in rows:
        slot = slots_by_id.get(r["slot"].split("/")[-1])
        if slot is None or slot.get("role") not in ("wall", "doorway", "window", "breach"):
            continue
        dims = slot["fit"]["dims"]
        exp_h = float(dims[2])
        sx, sy, sz = r["size"]
        horiz = sorted([round(sx, 2), round(sz, 2)])
        want = sorted([round(float(dims[0]), 2), round(float(dims[1]), 2)])
        # a scaled unit (wallEnd) carries its size in the transform; the AABB
        # is the truth either way
        if abs(sy - exp_h) <= tol:
            pose = "standing"
        elif abs(sy - float(dims[0])) <= tol or abs(sy - float(dims[1])) <= tol:
            pose = "spun"      # the module's width or thickness is vertical
        else:
            pose = "other"
        out.append({"slot": r["slot"], "mesh": r["mesh"], "pose": pose,
                    "height": round(sy, 2), "expected_height": exp_h,
                    "horizontal": horiz, "expected_horizontal": want,
                    "bottom_y": round(r["min"][1], 2),
                    "local_y_world": [round(v, 2) for v in r["local_y"]]})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("project")
    ap.add_argument("--scene", default="mission.tscn")
    ap.add_argument("--slots", default=None, help="the building's slots.json")
    ap.add_argument("--godot", default=None)
    ap.add_argument("--settle", type=int, default=5)
    ap.add_argument("--json", default=None, help="write every row here")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args(argv)
    try:
        report = census(a.project, scene=a.scene, godot=a.godot,
                        settle=a.settle, verbose=a.verbose)
    except ProbeFailed as exc:
        print(f"[module-pose] not measured: {exc}", file=sys.stderr)
        return 2
    rows = report["rows"]
    print(f"{len(rows)} mesh(es) under slot-named nodes")
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=1)
        print("wrote", a.json)
    if not a.slots:
        return 0
    slots = json.load(open(a.slots, encoding="utf-8"))["slots"]
    by_id = {s["slot_id"]: s for s in slots}
    judged = judge(rows, by_id)
    from collections import Counter
    print("wall-type poses:", dict(Counter(j["pose"] for j in judged)))
    bad = [j for j in judged if j["pose"] != "standing"]
    for j in bad[:25]:
        print(f"  {j['pose']:9} {j['slot']:24} {j['mesh']:28} height {j['height']:5.2f} "
              f"(slot {j['expected_height']:.2f})  horiz {j['horizontal']} (slot {j['expected_horizontal']})  "
              f"bottom y {j['bottom_y']:6.2f}  local Y -> {j['local_y_world']}")
    if len(bad) > 25:
        print(f"  ... and {len(bad) - 25} more")
    return 0


if __name__ == "__main__":
    sys.exit(main())
