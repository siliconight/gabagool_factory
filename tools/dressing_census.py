"""Count the Layer 3 surface dressing standing in a RUNNING exported package.

The export's `dressing_layer.json` says what it wrote; `export_closure_scan`
says every path resolves; the portability test says the entry scene
instantiated. None of them says the MultiMeshes are in the tree with their
instances and their meshes. This walks the running scene via godot_probe and
reports, per MultiMeshInstance3D: instance_count, visible instances, whether
the mesh resolved, and the world AABB of the instances -- so "1,094 instances"
is read off the engine rather than off the file that asked for them.

    python tools\\dressing_census.py <export_project> [--scene mission.tscn]

Prints what it measured and stops. A nonzero exit means only that the
measurement did not happen (no Godot, no project, no fence).
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from godot_probe import ProbeFailed, require_godot, run_probe   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PAYLOAD = os.path.join(HERE, "dressing_census.gd")   # a path: run_probe copies it
MARK_BEGIN = "<<<DRESSING_CENSUS_JSON"
MARK_END = "DRESSING_CENSUS_JSON>>>"


def census(project_dir, scene="mission.tscn", godot=None, settle=5,
           timeout=600, verbose=False):
    payload, _out, _mirror = run_probe(
        project_dir=project_dir, script_src=PAYLOAD,
        autoload_name="DressingCensus", scene="res://" + scene,
        begin=MARK_BEGIN, end=MARK_END, godot=godot or require_godot(),
        settings={"dressing_census": {"settle_frames": settle}},
        headless=True, timeout=timeout, verbose=verbose)
    return payload


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("project")
    ap.add_argument("--scene", default="mission.tscn")
    ap.add_argument("--godot", default=None)
    ap.add_argument("--settle", type=int, default=5)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args(argv)
    try:
        report = census(a.project, scene=a.scene, godot=a.godot,
                        settle=a.settle, verbose=a.verbose)
    except ProbeFailed as exc:
        print(f"[dressing-census] not measured: {exc}", file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(report, indent=1))
        return 0
    print(f"{report['multimesh_nodes']} MultiMeshInstance3D node(s), "
          f"{report['instances']} instances, {report['visible_instances']} visible")
    for n in report["nodes"]:
        p, s = n["aabb_position"], n["aabb_size"]
        box = (f"x {p[0]:.1f}..{p[0]+s[0]:.1f}  y {p[1]:.2f}..{p[1]+s[1]:.2f}  "
               f"z {p[2]:.1f}..{p[2]+s[2]:.1f}") if p else "no aabb"
        print(f"  {n['instance_count']:5} ({n['visible_instance_count']:5} visible)  "
              f"mesh={'yes' if n['mesh'] else 'NO'}  {box}  {n['path']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
