"""Show that a shipped level is navigable, and that its navigability follows
the body in `agent_contract.json`.

WHAT THIS IS FOR. The package ships `navmesh: bake_required` and no
`NavigationRegion3D`, so opening a level shows no navigation at all (roadmap
172 and its neighbours). This bakes one with the pipeline's own agent
dimensions, routes from the player start to every objective and extraction
anchor, and reports what it found -- so "our levels are navigable" is a
measurement somebody can check rather than a claim on a slide.

THE SECOND RUN IS THE POINT. `--compare RADIUS,HEIGHT` bakes the SAME package
again for a different body and prints the difference. That is the pipeline
being a pipeline: the level is not hand-fitted to one character, and the
navigable surface follows the contract. A bigger body loses the gaps it cannot
fit through, and the number of destinations it can still reach is the
interesting figure.

    python tools/navmesh_demo.py <package_dir>
    python tools/navmesh_demo.py <package_dir> --compare 0.55,1.95

WHAT THE COMPARISON DOES NOT SHOW, said here so nobody oversells it. Re-baking
moves the NAVIGABLE SURFACE for a different body over the SAME geometry. It
does not re-cut the doors. `agent_contract.json` also drives door widths,
corridor widths and stair clearances through Deli Counter, and those change
only when the shell library is rebuilt (`python build.py --all`, ~130 shells).
So this demonstrates half of the claim cheaply and honestly; the other half is
a rebuild, and saying which is which is the difference between a demo and a
sales pitch.

THE PARAMETERS COME FROM THE CONTRACT, never from this file. Godot's own bake
defaults would answer a different question -- 45 degrees of slope against this
pipeline's 55, while 20 of 38 buildings emit stair ramps between 45.0 and
51.3 -- so a default bake disconnects stairs this pipeline considers walkable.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTRACT = ROOT / "deli_counter" / "agent_contract.json"
SCRIPT = ROOT / "tools" / "navmesh_demo.gd"
REPORT = "navmesh_demo.json"


def _godot() -> str | None:
    import os
    for env in ("LF_GODOT", "DC_GODOT", "LOT_GODOT"):
        p = os.environ.get(env)
        if p and Path(p).is_file():
            return p
    usual = Path("C:/Godot/4.7/Godot_v4.7-stable_win64_console.exe")
    if usual.is_file():
        return str(usual)
    return shutil.which("godot")


def contract_agent() -> dict:
    """The bake parameters, from the one file that owns them.

    `nav_bake.agent_radius_m` is 0.40 and `characters.player.radius_m` is 0.35,
    and the contract's own note says why they differ: the mesh is baked for the
    fattest navigating character plus 0.05 so a 0.35 body has somewhere to
    stand. The BAKE parameter is the one a bake wants -- taking the body's
    would re-spend a safety margin the contract already spent, which is the
    confusion that cost two defects (roadmap 123).
    """
    d = json.loads(CONTRACT.read_text(encoding="utf-8"))
    nav = d["nav_bake"]
    return {
        "radius": float(nav["agent_radius_m"]),
        "height": float(nav["agent_height_m"]),
        "climb": float(nav["agent_max_climb_m"]),
        "slope": float(nav.get("agent_max_slope_deg", 55.0)),
        "cell": float(nav.get("cell_size_m", 0.10)),
        "cell_h": float(nav["cell_height_m"]),
    }


def bake(pkg: Path, agent: dict, godot: str, tag: str) -> dict:
    out = pkg / REPORT
    if out.exists():
        out.unlink()
    bundled = pkg / SCRIPT.name
    bundled.write_bytes(SCRIPT.read_bytes())
    try:
        subprocess.run(
            [godot, "--headless", "--path", str(pkg),
             "--script", f"res://{SCRIPT.name}", "--", f"res://{REPORT}",
             str(agent["radius"]), str(agent["height"]), str(agent["climb"]),
             str(agent["slope"]), str(agent["cell"]), str(agent["cell_h"])],
            capture_output=True, text=True, timeout=1800)
    finally:
        bundled.unlink(missing_ok=True)
    if not out.exists():
        raise SystemExit(f"navmesh_demo: {tag} bake wrote no report")
    rep = json.loads(out.read_text(encoding="utf-8"))
    out.unlink()
    if rep.get("schema") != "lf.navmesh_demo.v1":
        raise SystemExit(f"navmesh_demo: report schema {rep.get('schema')!r} "
                         f"is not the one this driver knows")
    return rep


def show(rep: dict, title: str) -> None:
    print(f"  {title}")
    a = rep["agent"]
    print(f"    body          radius {a['radius_m']:.2f} m, height "
          f"{a['height_m']:.2f} m, step {a['max_climb_m']:.2f} m, "
          f"slope {a['max_slope_deg']:.0f} deg")
    if not rep.get("ok"):
        print(f"    REFUSED       {rep.get('error')}")
        return
    print(f"    navmesh       {rep['polygons']} polygons, {rep['vertices']} "
          f"vertices, baked in {rep['bake_ms']:.0f} ms")
    print(f"    vertical      y {rep['mesh_y_min']:.2f} .. "
          f"{rep['mesh_y_max']:.2f} over {rep['storey_bands']} half-metre "
          f"band(s)  <- a one-floor mesh would read 1-2 here")
    print(f"    routes        {rep['reached']} of {rep['destinations']} "
          f"destination(s) reachable from the player start, "
          f"{rep['routes_that_climb']} of them climbing")
    if rep.get("stair_ramps"):
        print(f"    stairs        {rep['stair_ramps']} ramp(s), steepest "
              f"{rep['steepest_stair_deg']:.1f} deg, "
              f"{rep['stair_ramps_over_45deg']} over 45")
        if rep["stair_ramps_over_45deg"]:
            print("                  (connected by the bake, and a body whose "
                  "floor_max_angle is 45 slides back down those -- the "
                  "tension CLAUDE.md records, not a bug in this run)")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("package", type=Path)
    ap.add_argument("--compare", metavar="RADIUS,HEIGHT",
                    help="bake the same package again for a different body "
                         "and print the difference")
    ap.add_argument("--json", type=Path)
    args = ap.parse_args(argv)

    godot = _godot()
    if godot is None:
        print("navmesh_demo: no Godot binary (set DC_GODOT)")
        return 2
    if not args.package.is_dir():
        print(f"navmesh_demo: {args.package} is not a directory")
        return 2

    agent = contract_agent()
    print(f"navmesh_demo: {args.package}")
    print(f"  parameters from {CONTRACT.relative_to(ROOT)} -- the one file "
          f"that owns the body\n")
    base = bake(args.package, agent, godot, "contract")
    show(base, "AS SHIPPED, for this pipeline's agent")

    other = None
    if args.compare:
        r, h = (float(x) for x in args.compare.split(","))
        agent2 = dict(agent, radius=r, height=h)
        print()
        other = bake(args.package, agent2, godot, "compare")
        show(other, f"THE SAME LEVEL, re-derived for a {r:.2f} m x {h:.2f} m body")
        if base.get("ok") and other.get("ok"):
            print()
            print("  WHAT CHANGED, and why it is the point:")
            print(f"    polygons      {base['polygons']} -> {other['polygons']} "
                  f"({other['polygons'] - base['polygons']:+d})")
            print(f"    reachable     {base['reached']}/{base['destinations']}"
                  f" -> {other['reached']}/{other['destinations']}")
            print("    Nobody hand-fitted this level to either body. One "
                  "number changed and the navigable surface followed.")
            print("    (Door and corridor WIDTHS follow the same contract, but "
                  "only through a shell rebuild -- see this file's header.)")

    if args.json:
        args.json.write_text(json.dumps(
            {"package": str(args.package), "contract": base,
             "compare": other}, indent=1), encoding="utf-8")
        print(f"\n  wrote {args.json}")
    return 0 if base.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
