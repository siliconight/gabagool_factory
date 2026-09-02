"""Find walls that TERMINATE inside doorway apertures in a running scene.

The built-output half of roadmap 59. layout_lint L18 judges spec-authored
openings and the authored library now lints clean -- yet the sighting that
OPENED item 59 (a partition's WallEnd standing mid-aperture in
lot_demo_001's walk) is provably not in specs/: zero interior-host findings
library-wide. Its aperture is emitted downstream of the spec, so only the
composed, running scene can answer where it came from. This walks that tree
via godot_probe (mesh_light_census's pattern). The scene names doorway
FRAME pieces, not apertures -- the probe's own first run proved it by
matching any *Doorway* mesh and reporting 102 walls sitting FLUSH against
jambs, correct construction read as defects -- so each aperture is DERIVED:
the clear gap between a Doorway_Jamb_L / Doorway_Jamb_R pair under one
opening node. A visible mesh that is wall-shaped relative to that gap
(thin across it, long along the depth axis, reaching its plane, sharing
its height) whose thin extent sits strictly INSIDE the clear gap is a
wall ending inside a doorway.

    python tools\\door_split_probe.py <project_dir> [--scene X.tscn]

WHAT THE VERDICT DECIDES. If findings trace to generated/slot geometry, L18
must NOT graduate WARN -> FAIL until the generator learns avoidance; if the
tree is clean (or the findings are themed-kit emissions with their own
owner), graduation is safe. The probe prints measurements and paths; the
attribution argument happens in the reply, not in here.

WHAT A NONZERO EXIT MEANS. Only that the measurement did not happen: no
Godot, no project, no fence. A skip is never reported as a pass.

WHAT IT CANNOT SEE, stated plainly: apertures with no *Doorway*-named mesh
(the naming is the sensor), and walls that stop short of the span without
entering it.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from godot_probe import ProbeFailed, run_probe, require_godot   # noqa: E402
from mesh_light_census import default_scene                      # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PAYLOAD = os.path.join(HERE, "door_split_probe.gd")
MARK_BEGIN = "<<<DOOR_SPLIT_PROBE_JSON"
MARK_END = "DOOR_SPLIT_PROBE_JSON>>>"


def probe(project_dir, scene=None, godot=None, settle=5, timeout=600,
          verbose=False):
    scene = scene or default_scene(project_dir)
    payload, _out, _mirror = run_probe(
        project_dir=project_dir,
        script_src=PAYLOAD,
        autoload_name="DoorSplitProbe",
        scene="res://" + scene,
        begin=MARK_BEGIN, end=MARK_END,
        godot=godot or require_godot(),
        settings={"door_split_probe": {"settle_frames": settle}},
        headless=True, timeout=timeout, verbose=verbose)
    return payload


def report(c):
    if "error" in c:
        print("  probe error: " + str(c["error"]))
        return
    print("  scene            %s   (engine %s, settled %s frames)"
          % (c["scene"], c.get("engine", "?"), c["settle_frames"]))
    print("  apertures        %d derived from Doorway_Jamb_L/R pairs"
          % c["doorways"])
    print("  meshes           %d considered against them"
          % c["meshes_considered"])
    print("")
    print("  walls ending inside a doorway aperture: %d"
          % c["split_doorways"])
    for f in c.get("findings", []):
        px, py, pz = f["doorway_pos"]
        print("    at (%.1f, %.1f, %.1f)  span %.2f m  wall %.2f m off center"
              % (px, py, pz, f["span_width"], f["offset_from_center"]))
        print("      doorway: " + f["doorway"])
        print("      wall:    " + f["mesh"])
    groups = c.get("offender_groups", {})
    if groups:
        print("")
        print("  offending walls by tree location (the attribution data):")
        for k in sorted(groups, key=lambda g: -groups[g]):
            print("    %4d  %s" % (groups[k], k))


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="walls that terminate inside doorway apertures, measured "
                    "in the running composed scene")
    ap.add_argument("project", help="the Godot project folder to measure")
    ap.add_argument("--scene", default=None,
                    help="scene to run; default is the project's main scene")
    ap.add_argument("--godot", default=None)
    ap.add_argument("--settle", type=int, default=5)
    ap.add_argument("--json", action="store_true",
                    help="emit the raw payload instead of the table")
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args(argv)

    try:
        c = probe(a.project, a.scene, a.godot, a.settle, a.timeout, a.verbose)
    except ProbeFailed as e:
        print("[door_split_probe] NOT MEASURED: " + str(e))
        return 1

    if a.json:
        import json
        print(json.dumps(c, indent=2))
    else:
        print("[door_split_probe] " + os.path.abspath(a.project))
        report(c)

    if "error" not in c and int(c.get("doorways", 0)) == 0:
        print("")
        print("[door_split_probe] NO APERTURES: no Doorway_Jamb_L/R pair "
              "found under any node. This scene either has no doorway "
              "frames or names them differently -- a zero here is a blind "
              "sensor, not a clean building. Pass --scene, or check the "
              "naming.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
