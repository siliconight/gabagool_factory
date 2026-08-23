"""Count the positional lights that reach each MESH a scene actually runs.

WHAT THIS IS FOR. GL Compatibility budgets positional lights PER MESH
(`rendering/limits/opengl/max_lights_per_object`, engine default 8). A mesh
over the budget silently drops lights, which shows up standing still as a
hard brightness step where two slabs meet -- the seam level_factory's
per-object cap exists to paper over. Roadmap item 54 splits room-spanning
plates so every mesh fits the engine default, and this tool is the item's
closing instrument: the numbers that opened it came from module FILENAMES
(extents from `_w`/`_d`, rotation ignored), which can open an investigation
but cannot close one. This walks the running tree via godot_probe, takes
every visible mesh's world AABB, and counts the visible omni/spot lights
whose range reaches it -- the engine's own question, asked directly.

    python tools\\mesh_light_census.py <project_dir> [--scene X.tscn]

WHY IT IS NOT A GATE BY DEFAULT. The census prints and exits 0 whenever it
managed to measure. Pass --max-per-mesh 8 to make it fail a build; then the
number is a decision somebody made rather than one this file assumed on
their behalf. (`light_census.py` states the same policy for suns, and the
argument is the same.)

WHAT A NONZERO EXIT MEANS. Only that the measurement did not happen: no
Godot, no project, no fence. It never reports a skip as a pass.

WHAT THE COUNT OVERSTATES. Spot cones are ignored (range as a sphere), and a
light behind a wall still counts if its range crosses the mesh's AABB --
both make the count an upper bound on what the engine will bind. A mesh
that passes at 8 here cannot drop a light in the renderer; one that fails
here may still render clean, and the fix for that is to look, not to trust.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from godot_probe import ProbeFailed, run_probe, require_godot   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PAYLOAD = os.path.join(HERE, "mesh_light_census.gd")
MARK_BEGIN = "<<<MESH_LIGHT_CENSUS_JSON"
MARK_END = "MESH_LIGHT_CENSUS_JSON>>>"


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
        autoload_name="MeshLightCensus",
        scene="res://" + scene,
        begin=MARK_BEGIN, end=MARK_END,
        godot=godot or require_godot(),
        settings={"mesh_light_census": {"settle_frames": settle}},
        headless=True, timeout=timeout, verbose=verbose)
    return payload


def _bucket(histogram, lo, hi=None):
    """Meshes whose light count is in [lo, hi] (hi None = unbounded)."""
    total = 0
    for count, meshes in histogram.items():
        c = int(count)
        if c >= lo and (hi is None or c <= hi):
            total += int(meshes)
    return total


def report(c):
    """Print the census. Measurements and units; no verdict sentence."""
    if "error" in c:
        print("  probe error: " + str(c["error"]))
        return
    print("  scene            " + str(c["scene"]) +
          "   (engine " + str(c.get("engine", "?")) +
          ", settled " + str(c["settle_frames"]) + " frames)")
    print("  lights           %d positional visible, %d directional visible"
          % (c["positional_lights"], c["directional_visible"]))
    print("  project caps     max_lights_per_object=%d  "
          "max_renderable_lights=%d"
          % (c["cap_per_object"], c["cap_renderable"]))

    h = c["histogram"]
    print("")
    print("  meshes           %d visible" % c["meshes"])
    print("    <=8 lights     %d" % _bucket(h, 0, 8))
    print("    over 8         %d" % _bucket(h, 9))
    print("    over 16        %d" % _bucket(h, 17))
    print("    over 32        %d" % _bucket(h, 33))
    print("    worst          %d   %s" % (c["worst"], c["worst_path"]))

    rows = c.get("over_rows", [])
    if rows:
        print("")
        print("  meshes over the engine default of 8:")
        for row in rows:
            size = "x".join("%.1f" % v for v in row["size"])
            print("    %3d  %-14s %s" % (row["lights"], size, row["path"]))
        if c.get("over_rows_truncated"):
            print("    ... list truncated; the histogram above is complete")


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="per-mesh census of the positional lights that reach "
                    "each mesh a generated scene runs with")
    ap.add_argument("project", help="the Godot project folder to measure")
    ap.add_argument("--scene", default=None,
                    help="scene to run; default is the single *_walk.tscn")
    ap.add_argument("--godot", default=None,
                    help="path to the Godot binary; default LOT_GODOT, then "
                         "DC_GODOT, then the usual install locations, then PATH")
    ap.add_argument("--settle", type=int, default=5,
                    help="frames to wait before counting (default: %(default)s)")
    ap.add_argument("--max-per-mesh", type=int, default=None,
                    help="fail with exit 2 if any mesh sees more than N "
                         "positional lights. Off by default -- the right "
                         "number is a decision about the level, not about "
                         "this tool. Roadmap 54 closes at 8.")
    ap.add_argument("--json", action="store_true",
                    help="emit the raw census instead of the table")
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args(argv)

    try:
        c = census(a.project, a.scene, a.godot, a.settle, a.timeout, a.verbose)
    except ProbeFailed as e:
        print("[mesh_light_census] NOT MEASURED: " + str(e))
        return 1

    if a.json:
        import json
        print(json.dumps(c, indent=2))
    else:
        print("[mesh_light_census] " + os.path.abspath(a.project))
        report(c)

    if a.max_per_mesh is not None and "error" not in c:
        if int(c["worst"]) > a.max_per_mesh:
            print("")
            print("[mesh_light_census] MESH_LIGHTS_OVER_LIMIT: worst mesh "
                  "sees " + str(c["worst"]) + " positional lights against a "
                  "declared limit of " + str(a.max_per_mesh) + ".")
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
