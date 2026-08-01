"""Count the lights a generated scene actually RUNS with, not the ones it declares.

WHAT THIS IS FOR. Everything in this toolchain that checks lighting checks the
scene file. The scene file is a statement of intent; a level is lit by whatever
is in the tree at frame five, and the two came apart badly enough to cost a day.
`lux_inject` wrote `sun_light = NodePath("../Sun")` into the .tscn and Godot
discarded it in silence, because a Node-typed export is only resolved when the
[node] header names it in `node_paths` -- so the file said one sun and the
running level had two, at different angles, cross-hatching their self-shadowing
into a band along every grazing surface. Nothing in the repo could see that,
because nothing looked at the running tree.

    python tools\\light_census.py <project_dir> [--scene X.tscn]

WHY IT IS NOT A GATE BY DEFAULT. Two directional lights is a defect in a Lux
scene and perfectly correct in a scene with a deliberate fill light. This prints
the census and exits 0 whenever it managed to measure. Pass --max-directional to
make it fail a build, and then the number is a decision somebody made rather
than one this file assumed on their behalf.

WHAT A NONZERO EXIT MEANS. Only that the measurement did not happen: no Godot,
no project, no fence. It never reports a skip as a pass -- `walktest.py` shipped
that way once and a stage that could not run kept saying `succeeded`.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from godot_probe import ProbeFailed, run_probe, require_godot   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PAYLOAD = os.path.join(HERE, "light_census.gd")
MARK_BEGIN = "<<<LIGHT_CENSUS_JSON"
MARK_END = "LIGHT_CENSUS_JSON>>>"

#: Godot's Environment.tonemap_mode enum, so the report reads as words. Kept
#: here rather than in the .gd because the probe should ship raw numbers -- a
#: probe that names things has an opinion about them.
TONEMAP = {0: "LINEAR", 1: "REINHARD", 2: "FILMIC", 3: "ACES", 4: "AGX"}


def default_scene(project_dir):
    """The single *_walk.tscn, the way lux_inject.py picks one."""
    walks = sorted(f for f in os.listdir(project_dir)
                   if f.endswith("_walk.tscn"))
    if len(walks) != 1:
        raise ProbeFailed(
            "expected exactly one *_walk.tscn in " + project_dir + ", found " +
            str(len(walks)) + ": " + str(walks) + ". Pass --scene.")
    return walks[0]


def census(project_dir, scene=None, godot=None, settle=5, timeout=600,
           verbose=False):
    scene = scene or default_scene(project_dir)
    payload, _out, _mirror = run_probe(
        project_dir=project_dir,
        script_src=PAYLOAD,
        autoload_name="LightCensus",
        scene="res://" + scene,
        begin=MARK_BEGIN, end=MARK_END,
        godot=godot or require_godot(),
        settings={"light_census": {"settle_frames": settle}},
        headless=True, timeout=timeout, verbose=verbose)
    return payload


def report(c):
    """Print the census. Measurements and units; no verdict sentence."""
    if "error" in c:
        print("  probe error: " + str(c["error"]))
        return
    print("  scene            " + str(c["scene"]) +
          "   (engine " + str(c.get("engine", "?")) +
          ", settled " + str(c["settle_frames"]) + " frames)")

    d = c["directional"]
    print("")
    print("  DirectionalLight3D  " + str(len(d)))
    for row in d:
        line = ("    %-30s energy=%.3f  elev=%+6.1f deg  shadow=%s  visible=%s"
                % (row["path"], row["energy"], row["elevation_deg"],
                   str(row["shadow_enabled"]), str(row["visible_in_tree"])))
        print(line)
    casters = [r for r in d if r["shadow_enabled"] and r["visible_in_tree"]]
    print("    shadow casters visible: " + str(len(casters)))

    p = c["positional"]
    print("")
    print("  OmniLight3D  %d (%d visible)     SpotLight3D  %d (%d visible)"
          % (p["omni_total"], p["omni_visible"],
             p["spot_total"], p["spot_visible"]))

    print("")
    print("  WorldEnvironment  " + str(len(c["environments"])))
    for row in c["environments"]:
        if not row.get("has_environment"):
            print("    %-30s (no Environment resource)" % row["path"])
            continue
        tm = TONEMAP.get(row.get("tonemap_mode"), str(row.get("tonemap_mode")))
        print("    %-30s tonemap=%s exposure=%.3f white=%.3f ambient=%.3f "
              "glow=%s fog=%s"
              % (row["path"], tm, row["tonemap_exposure"], row["tonemap_white"],
                 row["ambient_light_energy"], str(row["glow_enabled"]),
                 str(row["fog_enabled"])))

    print("")
    print("  LuxRoot  " + str(len(c["lux_roots"])))
    for row in c["lux_roots"]:
        link = row["sun_light"] if row["sun_link_resolved"] else "<null>"
        print("    %-30s sun_light=%s" % (row["path"], link))
        print("      children: " +
              ", ".join(k["name"] + "(" + k["class"] + ")"
                        for k in row["children"]))
        print("      own DirectionalLight3D %d   own CanvasLayer %d"
              % (row["child_directional_lights"], row["child_canvas_layers"]))

    if c["duplicate_names"]:
        print("")
        print("  sibling name collisions  " + str(len(c["duplicate_names"])))
        for row in c["duplicate_names"]:
            print("    %-30s %s x%d"
                  % (row["parent"], row["base_name"], row["count"]))


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="census of the lights and environments a generated scene "
                    "runs with")
    ap.add_argument("project", help="the Godot project folder to measure")
    ap.add_argument("--scene", default=None,
                    help="scene to run; default is the single *_walk.tscn")
    ap.add_argument("--godot", default=None,
                    help="path to the Godot binary; default LOT_GODOT, then "
                         "DC_GODOT, then the usual install locations, then PATH")
    ap.add_argument("--settle", type=int, default=5,
                    help="frames to wait before counting (default: %(default)s)")
    ap.add_argument("--max-directional", type=int, default=None,
                    help="fail with exit 2 if more than N DirectionalLight3D "
                         "are visible. Off by default -- the right number is a "
                         "decision about the level, not about this tool")
    ap.add_argument("--json", action="store_true",
                    help="emit the raw census instead of the table")
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args(argv)

    try:
        c = census(a.project, a.scene, a.godot, a.settle, a.timeout, a.verbose)
    except ProbeFailed as e:
        print("[light_census] NOT MEASURED: " + str(e))
        return 1

    if a.json:
        import json
        print(json.dumps(c, indent=2))
    else:
        print("[light_census] " + os.path.abspath(a.project))
        report(c)

    if a.max_directional is not None:
        visible = [r for r in c.get("directional", []) if r["visible_in_tree"]]
        if len(visible) > a.max_directional:
            print("")
            print("[light_census] LIGHT_CENSUS_DIRECTIONAL_OVER_LIMIT: "
                  + str(len(visible)) + " visible DirectionalLight3D against a "
                  "declared limit of " + str(a.max_directional) + ".")
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
