"""Census: does each library shell keep its walkable connections wherever it
lands on the voxel grid?

Each shell is baked alone at several grid origins with the site's navmesh
settings (grid_census.gd; cell 0.1, height 0.15, radius 0.4, climb 0.15,
slope 55, meshes and colliders, as Lot's site bake). The points tested are
the shell's interior gameplay markers and its stairs' nav endpoints. For
every pair of points that stands on the navmesh at every origin, the pair is
CONNECTED, CUT or SPLIT, the last meaning it is connected at some origins
and not at others. A split pair is the defect: whether it holds in a level
depends on where the shell lands.

    python grid_census.py [--only a,b] [--out census.json]

Interior only: a shell is baked without the street, so markers outside its
footprint stand on nothing, and they are left out rather than called cut.
Prints what it measured and names no cause. A shell whose row never came
back is listed as NOT MEASURED, never as clean.
"""
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import godot_probe  # noqa: E402

BUILD = ROOT / "deli_counter" / "build"
# Markers that stand on a floor a body walks to. Wall sockets (camera,
# door, key), vertical links (ladder, hatch) and street points (attacker
# spawn, extraction) are not floor positions inside one building.
FLOOR_TYPES = {"objective", "defender_spawn", "loot", "patrol_point",
               "crew_spawn", "stronghold", "cover_low", "cover_high",
               "landmark", "responder_spawn", "horde_spawn"}
# Eight grid origins: eight distinct X and eight distinct Z offsets inside
# one 0.1 m cell, and four Y offsets inside one 0.15 m cell.
OFFSETS = [[0.0, 0.0, 0.0], [0.05, 0.075, 0.025], [0.025, 0.0, 0.075],
           [0.075, 0.075, 0.05], [0.0125, 0.0375, 0.0375],
           [0.0625, 0.1125, 0.0125], [0.0375, 0.0375, 0.0875],
           [0.0875, 0.1125, 0.0625]]
PAD = 2.0


def godot_xyz(x, y, z):
    """Deli Counter level space (Z up, +Y north) -> Godot (Y up)."""
    return [x, z, -y]


def shell_points(gp):
    w, d = gp.get("footprint") or [0, 0]
    pts = {}
    for i, m in enumerate(gp.get("markers", [])):
        if m.get("type") not in FLOOR_TYPES:
            continue
        x, y, z = float(m["x"]), float(m["y"]), float(m.get("z", 0.0))
        if abs(x) > w / 2.0 - 0.2 or abs(y) > d / 2.0 - 0.2:
            continue
        pts["%s#%d" % (m.get("name") or m.get("type"), i)] = godot_xyz(x, y, z)
    for s in gp.get("stair_systems", []):
        eps = s.get("nav_endpoints") or {}
        if s.get("role") == "decorative_nontraversable":
            continue
        for end in ("lower", "upper"):
            if eps.get(end):
                x, y, z = (float(v) for v in eps[end])
                pts["stair:%s:%s" % (s.get("id", "?"), end)] = godot_xyz(x, y, z)
    return pts


def analyse(row, names):
    bakes = row["bakes"]
    n = len(bakes)
    isl = {p: [b["islands"][p] for b in bakes] for p in names}
    on_mesh = [p for p in names if all(v >= 0 for v in isl[p])]
    flicker = [p for p in names if any(v >= 0 for v in isl[p]) and any(v < 0 for v in isl[p])]
    never = [p for p in names if all(v < 0 for v in isl[p])]
    split = []
    for i, a in enumerate(on_mesh):
        for b in on_mesh[i + 1:]:
            k = sum(1 for o in range(n) if isl[a][o] == isl[b][o])
            if 0 < k < n:
                split.append((a, b, k))
    return {"points": len(names), "on_mesh": len(on_mesh), "flicker": flicker,
            "never": never, "split": split, "origins": n,
            "polys": [b["polys"] for b in bakes]}


def main():
    argv = sys.argv[1:]
    only = set(argv[argv.index("--only") + 1].split(",")) if "--only" in argv else None
    out_path = pathlib.Path(argv[argv.index("--out") + 1]) if "--out" in argv else HERE / "census.json"
    shells, skipped = {}, []
    for gp_path in sorted(BUILD.glob("*.gameplay.json")):
        name = gp_path.name[:-len(".gameplay.json")]
        if only and name not in only:
            continue
        if not (BUILD / (name + ".glb")).is_file():
            skipped.append((name, "no glb"))
            continue
        pts = shell_points(json.loads(gp_path.read_text(encoding="utf-8")))
        if len(pts) < 2:
            skipped.append((name, "%d point(s)" % len(pts)))
            continue
        shells[name] = {"glb": "res://shells/%s.glb" % name, "points": pts}
    print("shells to measure: %d; skipped: %d" % (len(shells), len(skipped)), flush=True)

    proj = pathlib.Path(tempfile.mkdtemp(prefix="grid_census_"))
    try:
        (proj / "shells").mkdir()
        for name in shells:
            shutil.copy2(BUILD / (name + ".glb"), proj / "shells" / (name + ".glb"))
        (proj / "project.godot").write_text(
            'config_version=5\n\n[application]\n\nconfig/name="grid_census"\n'
            'config/features=PackedStringArray("4.7")\n', encoding="utf-8")
        (proj / "probe_empty.tscn").write_text(
            '[gd_scene format=3]\n\n[node name="probe_empty" type="Node3D"]\n',
            encoding="utf-8")
        (proj / "census_points.json").write_text(json.dumps(
            {"offsets": OFFSETS, "pad": PAD, "shells": shells}), encoding="utf-8")
        godot_probe.add_autoload(str(proj), str(HERE / "grid_census.gd"), "GridCensus")
        godot = godot_probe.require_godot()
        t0 = time.time()
        r = subprocess.run([godot, "--headless", "--path", str(proj), "--import"],
                           capture_output=True, text=True, timeout=3600)
        print("import: exit %d, %.0f s" % (r.returncode, time.time() - t0), flush=True)
        rows = {}
        proc = subprocess.Popen([godot, "--headless", "--path", str(proj), "res://probe_empty.tscn"],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                encoding="utf-8", errors="replace")
        done = False
        for line in proc.stdout:
            if line.startswith("CENSUS_ROW "):
                row = json.loads(line[len("CENSUS_ROW "):])
                rows[row["shell"]] = row
                print("  %3d/%d %s" % (len(rows), len(shells), row["shell"]), flush=True)
            elif line.startswith("CENSUS_DONE"):
                done = True
        proc.wait(timeout=600)
    finally:
        shutil.rmtree(proj, ignore_errors=True)

    report = {"offsets": OFFSETS, "pad": PAD, "complete": done, "skipped": skipped,
              "not_measured": sorted(set(shells) - set(rows)), "shells": {}}
    for name, row in sorted(rows.items()):
        if "error" in row:
            report["shells"][name] = {"error": row["error"]}
            continue
        report["shells"][name] = analyse(row, list(shells[name]["points"]))
    out_path.write_text(json.dumps(report, indent=1), encoding="utf-8")

    split_shells = {k: v for k, v in report["shells"].items() if v.get("split")}
    flicker_shells = {k: v for k, v in report["shells"].items() if v.get("flicker")}
    print("\nmeasured %d of %d shells at %d grid origins (complete: %s)"
          % (len(rows), len(shells), len(OFFSETS), done))
    print("NOT MEASURED: %s" % (", ".join(report["not_measured"]) or "none"))
    print("shells with a SPLIT pair (connected at some origins, not all): %d" % len(split_shells))
    for name, v in sorted(split_shells.items(), key=lambda kv: -len(kv[1]["split"])):
        pts = sorted({p for a, b, k in v["split"] for p in (a, b)})
        ks = sorted({k for a, b, k in v["split"]})
        print("  %-28s %3d split pair(s), connected at %s of %d origins; points: %s"
              % (name, len(v["split"]), ks, v["origins"], ", ".join(pts)[:300]))
    print("shells with a point on the mesh at some origins only: %d" % len(flicker_shells))
    for name, v in sorted(flicker_shells.items()):
        print("  %-28s %s" % (name, ", ".join(v["flicker"])[:300]))
    print("report: %s" % out_path)


if __name__ == "__main__":
    main()
