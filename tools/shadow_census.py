"""Which lights in a RUNNING package cast shadows, by rig class.

Roadmap 60's policy (Lux 0.32.0) enables shadow maps on the
`max_shadow_casters` highest-ranked rig lights -- area rigs on the envelope
first, then bare bulbs, then exterior packs and streetlights, then the
fluorescent rows -- and disables them on the rest. This reads the result off
the engine: how many lights, how many shadowed, per class, and the tier and
budget the LuxRoot in the scene is running.

    python tools\\shadow_census.py <export_project> [--scene mission.tscn]

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
PAYLOAD = os.path.join(HERE, "shadow_census.gd")   # a path: run_probe copies it
MARK_BEGIN = "<<<SHADOW_CENSUS_JSON"
MARK_END = "SHADOW_CENSUS_JSON>>>"


def census(project_dir, scene="mission.tscn", godot=None, settle=5,
           timeout=600, verbose=False):
    payload, _out, _mirror = run_probe(
        project_dir=project_dir, script_src=PAYLOAD,
        autoload_name="ShadowCensus", scene="res://" + scene,
        begin=MARK_BEGIN, end=MARK_END, godot=godot or require_godot(),
        settings={"shadow_census": {"settle_frames": settle}},
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
        print(f"[shadow-census] not measured: {exc}", file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(report, indent=1))
        return 0
    print(f"{report['lights']} lights, {report['shadowed']} shadowed; "
          f"LuxRoot tier {report['tier']}, budget {report['budget']}")
    for cls, row in sorted(report["by_class"].items()):
        print(f"  {cls:12} {row['shadowed']:3} of {row['lights']:3} shadowed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
