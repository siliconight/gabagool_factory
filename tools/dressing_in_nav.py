"""Is the dressing standing where a body walks? Ask the baked navmesh.

WHAT THIS IS FOR, and why it lives here rather than in Patina. The standing
rule is "no dressing in walkable space or firing lines". Patina enforces the
half it can see: `openings.keep_out_boxes` clears the lane through a door or
window, and `openings.room_boxes` clears room interiors. Both read ONE
building's slots.json and gameplay.json, and that is a ceiling, not an
oversight -- a pilaster 5 cm proud is legal on its own facade and becomes an
obstruction the moment Lot places another building 1.2 m away and the gap
between them becomes a route. The alley is a site fact. No per-building rule
reaches it however good its arithmetic, and a report of "0 intrusions" from
those rules means the rooms are clean, not that the rule is satisfied.

The baked `NavigationRegion3D` is the answer to "where can a body go". It is
baked from the assembled site, it carries the same 0.4 m agent radius the rest
of the pipeline quotes, and it exists only after `lot_assemble`. So this runs
against an assembled walk project, not a manifest.

    python tools\\dressing_in_nav.py <walk_project> [--scene site_walk.tscn]

Build the project with `tools/walk_themed.py --godot ...` first. WITHOUT the
import pass the GLBs never import, the building fails to load entirely, and
this measures an empty scene while reporting a clean result.

WHAT THE TEST IS. For each `Cover_*` mesh, its world AABB tested against every
walkable sample between step height and head height above the floor. Bounded
vertically because a curb you step over is not an obstruction and a gutter
three metres up is not either.

NO HORIZONTAL MARGIN, and that was a correction. The first version grew the box
by the agent radius, on the reasoning that a body does not have to share a
coordinate with geometry to collide with it. True, and already handled: Godot's
navmesh bake INSETS walkable surface by the agent radius, so a nav sample is a
position the body already fits in. Adding the radius again applies it twice and
flags every cover mounted flat on a wall -- measured, 990+ offenders each with
exactly 2 samples, the two nearest polygon vertices sitting on the boundary.
`--agent-radius` still exists for an extra margin on top; 0.0 is the honest
default.

WHAT IT CANNOT TELL YOU. Firing lines. A shot travels where a body cannot, so
the navmesh under-reports the rule by design -- window lanes are Patina's half
of that and this is not a substitute for them. It also cannot tell a placement
bug from a prop you are meant to brush past; it reports where things are.

WHAT A NONZERO EXIT MEANS. The measurement did not happen: no Godot, no
project, no navmesh. Dressing in the walk volume is a finding and exits 0.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from godot_probe import ProbeFailed, require_godot, run_probe  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PAYLOAD = os.path.join(HERE, "dressing_in_nav.gd")
MARK_BEGIN = "<<<DRESSING_NAV_JSON"
MARK_END = "DRESSING_NAV_JSON>>>"


def default_scene(project_dir):
    """The single *_walk.tscn, the way light_census picks one."""
    walks = sorted(f for f in os.listdir(project_dir)
                   if f.endswith("_walk.tscn"))
    if len(walks) != 1:
        raise ProbeFailed(
            "expected exactly one *_walk.tscn in " + project_dir + ", found "
            + str(len(walks)) + ": " + str(walks) + ". Pass --scene.")
    return walks[0]


def probe(project_dir, scene=None, godot=None, settle=5, agent_radius=0.0,
          step_clear=0.15, body_height=1.8, prefix="Cover_", timeout=900,
          verbose=False):
    scene = scene or default_scene(project_dir)
    payload, _out, _mirror = run_probe(
        project_dir=project_dir,
        script_src=PAYLOAD,
        autoload_name="DressingNav",
        scene="res://" + scene,
        begin=MARK_BEGIN, end=MARK_END,
        godot=godot or require_godot(),
        settings={"dressing_nav": {
            "settle_frames": settle, "agent_radius": agent_radius,
            "step_clear": step_clear, "body_height": body_height,
            "prefix": prefix}},
        headless=True, timeout=timeout, verbose=verbose)
    return payload


def report(r, list_n=15):
    if "error" in r:
        print("  probe error: " + str(r["error"]))
        return
    print("  scene %s   engine %s" % (r["scene"], r.get("engine", "?")))
    print("  body: radius %.2f m, clear %.2f m .. %.2f m above the floor"
          % (r["agent_radius"], r["step_clear"], r["body_height"]))
    print("")
    print("  NavigationRegion3D  %d" % len(r["nav_regions"]))
    parsed_names = {0: "MESH_INSTANCES", 1: "STATIC_COLLIDERS", 2: "BOTH"}
    circular = False
    for reg in r["nav_regions"]:
        note = ("   " + reg["note"]) if reg.get("note") else ""
        print("    %-28s polygons %d%s"
              % (reg["path"], reg.get("polygons", 0), note))
        if "parsed_geometry_type" in reg:
            pt = reg["parsed_geometry_type"]
            print("      parsed %s   agent r=%.2f h=%.2f   cell %.3f"
                  % (parsed_names.get(pt, str(pt)),
                     reg.get("bake_agent_radius", 0.0),
                     reg.get("bake_agent_height", 0.0),
                     reg.get("bake_cell_size", 0.0)))
            if pt in (0, 2):
                circular = True
    print("    walkable samples: %d" % r["nav_samples"])
    if r.get("baked_here"):
        print("    BAKED BY THIS PROBE (%d region(s) arrived empty). The walk "
              "project" % r["baked_here"])
        print("    ships an unbaked NavigationMesh, so this is the probe's own "
              "answer to")
        print("    'where can a body go', not Lot's. Treat it as indicative "
              "until Lot bakes.")
    print("")
    if not r["nav_samples"]:
        print("  NO WALKABLE SURFACE FOUND -- nothing was measured. A clean")
        print("  result here would mean the navmesh is missing, not that the")
        print("  dressing is clear.")
        return
    print("  %-18s %8s %10s %8s" % ("family", "covers", "in the way", "pct"))
    fams = sorted(r["by_family"].items(), key=lambda kv: -kv[1][1])
    for fam, (n, bad) in fams:
        print("  %-18s %8d %10d %7.1f%%"
              % (fam, n, bad, 100.0 * bad / n if n else 0.0))
    print("  %-18s %8d %10d %7.1f%%"
          % ("TOTAL", r["covers"], r["flagged"],
             100.0 * r["flagged"] / r["covers"] if r["covers"] else 0.0))
    print("")
    if not r["flagged"]:
        if circular:
            print("  0 IN THE WAY, AND THE TEST CANNOT SUPPORT IT. The bake "
                  "parsed MESH")
            print("  INSTANCES, so it carved the walkable surface AROUND the "
                  "dressing --")
            print("  no cover can overlap nav by construction and this zero is "
                  "circular.")
            print("  Re-bake parsing STATIC_COLLIDERS, which ignores the "
                  "covers (they carry")
            print("  no collision by contract), and the number becomes a "
                  "finding.")
        else:
            print("  No cover stands in walkable space.")
        return
    for o in r["offenders"][:list_n]:
        print("    %-22s at %s  size %s  (%d samples)"
              % (o["name"], o["pos"], o["size"], o["nav_samples"]))
    if r["flagged"] > len(r["offenders"]):
        print("    ... and %d more (only the first %d were recorded)"
              % (r["flagged"] - len(r["offenders"]), len(r["offenders"])))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("project", help="an assembled walk project")
    ap.add_argument("--scene", default=None)
    ap.add_argument("--godot", default=None)
    ap.add_argument("--settle", type=int, default=5)
    ap.add_argument("--agent-radius", type=float, default=0.0,
                    help="EXTRA horizontal margin, on top of what the navmesh "
                         "already encodes. Default 0.0, and 0.0 is right: "
                         "Godot's bake insets walkable surface by the agent "
                         "radius, so a nav sample is a place the body ALREADY "
                         "fits. Passing 0.4 here applies the radius twice and "
                         "flags every cover flat on a wall -- measured, 990+ "
                         "offenders each reporting exactly 2 samples, which is "
                         "the two nearest polygon vertices on the boundary.")
    ap.add_argument("--step-clear", type=float, default=0.15,
                    help="below this above the floor is a step, not an "
                         "obstruction (default 0.15)")
    ap.add_argument("--body-height", type=float, default=1.8)
    ap.add_argument("--prefix", default="Cover_",
                    help="node-name prefix of the geometry to test; "
                         "'WallPack_' checks the light fixtures instead")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)

    try:
        r = probe(args.project, scene=args.scene, godot=args.godot,
                  settle=args.settle, agent_radius=args.agent_radius,
                  step_clear=args.step_clear, body_height=args.body_height,
                  prefix=args.prefix, timeout=args.timeout,
                  verbose=args.verbose)
    except ProbeFailed as exc:
        sys.stderr.write("[dressing_in_nav] NOT MEASURED: %s\n" % exc)
        return 2
    if args.json:
        print(json.dumps(r, indent=2))
        return 0
    print("=" * 68)
    print("[dressing_in_nav] " + os.path.abspath(args.project))
    report(r)
    print("")
    return 0


if __name__ == "__main__":
    sys.exit(main())
