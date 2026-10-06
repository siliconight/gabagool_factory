"""Where does a split shell's connection break? For each shell census.json
lists with a SPLIT pair: bake at the census's grid origins; take the route
between the pair at an origin where it connects, walk it at an origin where
it does not, and report where it leaves the start's island
(neck_finder.gd). Then name the openings, stair ends and collider nodes
nearest that point.

    python neck_finder.py [--only a,b] [--census census.json] [--build DIR] [--out necks.json]

`--build DIR` reads shells from a scratch build (through grid_census). With
`--build` or `--only`, `--out` is required: necks.json is the library's record.

Prints what it measured -- where the route breaks (level space: x, y north, z
up), the island sequence along it, and what stands nearest. It does not say
which of those is the cause.

SUPERSEDED, KEPT: the first version reported the closest approach between
the two islands, which measures the thinnest wall between them as readily as
the neck (necks_closest_approach.txt).
"""
import json
import pathlib
import shutil
import struct
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import grid_census as gc  # noqa: E402

godot_probe = gc.godot_probe
MARKER_MAX_ABOVE = 0.45   # nav_gate.gd: 0.3 + agent_max_climb
NO_CEILING = 1.0e9        # stair ends, as the gate snaps them


def pick_pairs(split, limit=2):
    """Up to `limit` split pairs sharing no point, so two necks can show."""
    out, used = [], set()
    for a, b, k in sorted(split, key=lambda t: t[2]):
        if a in used or b in used:
            continue
        out.append((a, b))
        used |= {a, b}
        if len(out) >= limit:
            break
    return out


def glb_colliders(path):
    """(name, centre, half-size) in level space for collider-named nodes with
    a mesh. Translation and mesh bounds only -- these shells' colliders are
    unrotated boxes and slabs, and a rotated one is reported at its centre."""
    b = path.read_bytes()
    n = struct.unpack_from("<I", b, 12)[0]
    gl = json.loads(b[20:20 + n])
    out = []
    for nd in gl.get("nodes", []):
        name = nd.get("name", "")
        if "col" not in name.lower() or "mesh" not in nd:
            continue
        acc_ids = [p["attributes"]["POSITION"] for p in gl["meshes"][nd["mesh"]]["primitives"]]
        lo = [min(gl["accessors"][a]["min"][i] for a in acc_ids) for i in range(3)]
        hi = [max(gl["accessors"][a]["max"][i] for a in acc_ids) for i in range(3)]
        t = nd.get("translation", [0, 0, 0])
        c = [t[i] + (lo[i] + hi[i]) / 2.0 for i in range(3)]
        h = [(hi[i] - lo[i]) / 2.0 for i in range(3)]
        # Godot (x, y up, z) -> level (x, y north = -z, z up = y)
        out.append((name, (c[0], -c[2], c[1]), (h[0], h[2], h[1])))
    return out


def nearest(gp, cols, at):
    x, y, z = at
    rows = []
    for o in gp.get("openings", []):
        floor = float(o.get("z", 0.0)) - float(o.get("height", 0.0) or 0.0) / 2.0
        if abs(floor - z) > 1.0:
            continue
        d = ((float(o["x"]) - x) ** 2 + (float(o["y"]) - y) ** 2) ** 0.5
        rows.append((d, "%s %s %.2fm on %s at (%.2f, %.2f)%s" % (
            o.get("kind"), o.get("tag") or "", float(o.get("width") or 0.0),
            o.get("wall"), float(o["x"]), float(o["y"]),
            " [breach panel]" if o.get("kind") == "breach" else "")))
    for s in gp.get("stair_systems", []):
        for end, p in ((s.get("nav_endpoints") or {}).items()):
            if p and abs(float(p[2]) - z) <= 1.0:
                d = ((float(p[0]) - x) ** 2 + (float(p[1]) - y) ** 2) ** 0.5
                rows.append((d, "stair %s %s end at (%.2f, %.2f)" % (s.get("id"), end, p[0], p[1])))
    for name, c, h in cols:
        if c[2] + h[2] < z - 0.3 or c[2] - h[2] > z + 2.0:
            continue
        dx = max(abs(x - c[0]) - h[0], 0.0)
        dy = max(abs(y - c[1]) - h[1], 0.0)
        rows.append(((dx * dx + dy * dy) ** 0.5, "collider %s, box %.2f x %.2f centred (%.2f, %.2f)"
                     % (name, 2 * h[0], 2 * h[1], c[0], c[1])))
    return sorted(rows)[:6]


def main():
    argv = sys.argv[1:]
    only = set(argv[argv.index("--only") + 1].split(",")) if "--only" in argv else None
    out_path = pathlib.Path(argv[argv.index("--out") + 1]) if "--out" in argv else HERE / "necks.json"
    # A scratch run once wrote twin_a01's two rows over the library's 22 here
    # (kept as necks_twin_exp.json); the record is restored from git.
    if out_path == HERE / "necks.json" and ("--build" in argv or only):
        sys.exit("--build or --only measures part of the record: pass --out, so necks.json "
                 "stays the library's")
    cpath = HERE / (argv[argv.index("--census") + 1] if "--census" in argv else "census.json")
    census = json.loads(cpath.read_text(encoding="utf-8"))
    cases, gps = [], {}
    for shell, v in sorted(census["shells"].items()):
        if not v.get("split") or (only and shell not in only):
            continue
        gp = json.loads((gc.BUILD / (shell + ".gameplay.json")).read_text(encoding="utf-8"))
        gps[shell] = gp
        pts = gc.shell_points(gp)
        for a, b in pick_pairs(v["split"]):
            cases.append({"shell": shell, "glb": "res://shells/%s.glb" % shell,
                          "a": pts[a], "b": pts[b], "pair": [a, b],
                          "above_a": NO_CEILING if a.startswith("stair:") else MARKER_MAX_ABOVE,
                          "above_b": NO_CEILING if b.startswith("stair:") else MARKER_MAX_ABOVE})
    print("cases: %d across %d shells (from %s)" % (len(cases), len(gps), cpath.name), flush=True)
    proj = pathlib.Path(tempfile.mkdtemp(prefix="neck_finder_"))
    rows, done = [], False
    try:
        (proj / "shells").mkdir()
        for shell in gps:
            shutil.copy2(gc.BUILD / (shell + ".glb"), proj / "shells" / (shell + ".glb"))
        (proj / "project.godot").write_text(
            'config_version=5\n\n[application]\n\nconfig/name="neck_finder"\n'
            'config/features=PackedStringArray("4.7")\n', encoding="utf-8")
        (proj / "probe_empty.tscn").write_text(
            '[gd_scene format=3]\n\n[node name="probe_empty" type="Node3D"]\n', encoding="utf-8")
        (proj / "neck_points.json").write_text(json.dumps(
            {"offsets": gc.OFFSETS, "pad": gc.PAD, "cases": cases}), encoding="utf-8")
        godot_probe.add_autoload(str(proj), str(HERE / "neck_finder.gd"), "NeckFinder")
        godot = godot_probe.require_godot()
        subprocess.run([godot, "--headless", "--path", str(proj), "--import"],
                       capture_output=True, text=True, timeout=1800)
        r = subprocess.run([godot, "--headless", "--path", str(proj), "res://probe_empty.tscn"],
                           capture_output=True, text=True, timeout=3600,
                           encoding="utf-8", errors="replace")
        for line in (r.stdout or "").splitlines():
            if line.startswith("NECK_ROW "):
                rows.append(json.loads(line[len("NECK_ROW "):]))
        done = "NECK_DONE" in (r.stdout or "")
    finally:
        shutil.rmtree(proj, ignore_errors=True)
    print("rows: %d of %d (complete: %s)\n" % (len(rows), len(cases), done))
    for row in rows:
        shell = row["shell"]
        conn = row.get("connected", [])
        print("%s  %s <-> %s  connected at %d of %d" % (
            shell, row["pair"][0], row["pair"][1], sum(1 for c in conn if c), len(conn)))
        neck = row.get("neck") or {}
        if not neck.get("found"):
            print("    %s" % (neck.get("why") or row.get("note") or json.dumps(row)[:200]))
            continue
        gx, gy, gz = neck["at"]
        at = (gx, -gz, gy)  # Godot -> level space
        row["level_at"] = at
        print("    breaks %.1f m along a %.1f m route at level (%.2f, %.2f, z %.2f); "
              "pass origin %s, fail origin %s" % (neck["along_m"], neck["route_m"], at[0], at[1],
                                                  at[2], row.get("pass_offset"), row.get("fail_offset")))
        print("    islands along the route at the failing origin: %s" % neck["sequence"][:160])
        cols = glb_colliders(gc.BUILD / (shell + ".glb"))
        for d, what in nearest(gps[shell], cols, at):
            print("      %5.2f m  %s" % (d, what))
    out_path.write_text(json.dumps(rows, indent=1), encoding="utf-8")
    print("\nreport: %s" % out_path)


if __name__ == "__main__":
    main()
