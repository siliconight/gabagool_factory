"""Do a rowhome's stoop and its railings change what the graders grade? (Factory roadmap 240; the stoop
proposal's pre-ship step, `docs/proposals/ROWHOUSE_STOOP.md`, never run for the stoops or the railings.)

    python docs/findings/stoop_breadth/build_flat.py                  # the two sets of shells, first
    python docs/findings/stoop_breadth/stoop_breadth.py --grader laser_tag|walk [--only LABEL ...]

THE LOTS. Every staged lot `docs/findings/route_snag/engine_breadth.py` reads that has rowhome Empties in
it: 8 of its 16 (deli_001's, gas_block_001's and crossroads_9600's have none, so a stoop cannot reach
their grade). Each is graded three times, the level exactly as staged but for its
`buildings/gs_empty_rowhome_*.glb`:

  flat    the twelve rowhomes as Deli Counter 0.212.0 builds them with `stoop=0` (`build_flat.py`)
  flat2   the same again: THE CONTROL -- it must read identically to `flat` in every field read, or the
          lot cannot separate a stoop from noise, and its row says so
  stoop   the twelve as Deli Counter 0.212.0 built them: three steps up, on a stoop with its railings

THE GRADERS.
- Laser Tag: today's addon in each copy (as `engine_breadth.py` does), `--fixed-fps 60`, 25 runs from
  the seed its job used, Godot Physics (the engine the game uses). Read: the grade, the score, every field
  of the summary, the pins (player-stuck events at one position, to a millimetre, recurring in two or more
  runs -- `engine_breadth.py`'s count) and the navmesh the run baked (its log's "Baked navmesh" line).
- The walk test: `lot/walktest.py`'s own steps in its `main()`'s order -- `ensure_project`, `sync_addon`
  (today's director, as every real run gets it), `import_pass`, `run_one`. Read: the verdict, each walker's
  status, the targets reached, the anchors' counts, the simulated seconds.
  RETRACTED, KEPT: the first version walked each copy's STAGED director, as `rewalk.py` does for the
  copies it patches. A director staged before Lot 0.117.0 (its navigation moved to its own thread) never
  saw its map settle under today's fixed clock: warehouse_yard_001 seed_9004's `flat` arm, with no stoop
  in it, read "navigation map is EMPTY at QA time" after 600 frames where its job settled in 7, the same
  2,340-polygon bake. Nothing here patches the director, so it gets today's, as `main()` gives it.

Writes `results_<grader>.json` beside this file (one row a lot and arm) and prints, for each lot, each
arm's row and every field `stoop` moved from `flat`. Prints what it measured and stops. Copies go to
`_scratch/stoop_breadth/<grader>/` and are removed once read.
"""
import argparse
import collections
import contextlib
import io
import json
import pathlib
import re
import shutil
import subprocess
import sys
import time

F = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
GODOT = "C:/Godot/4.7/Godot_v4.7-stable_win64_console.exe"
LT_ADDON = F / "lasertag" / "addons" / "laser_tag_tool"
SHELLS = F / "_scratch" / "stoop_breadth"
#: (workspace, mission, seed): `engine_breadth.py`'s lots with rowhome Empties in them
LOTS = [
    ("cold-9264-ws", "restaurant_row_001", "seed_9003"),
    ("cold-9264-ws", "restaurant_row_001", "seed_9104"),
    ("cold-9264-ws", "restaurant_row_001", "seed_9205"),
    ("cold-9240-ws", "warehouse_yard_001", "seed_9004"),
    ("cold-9240-ws", "warehouse_yard_001", "seed_9105"),
    ("cold-9240-ws", "warehouse_yard_001", "seed_9206"),
    ("cold-9214-ws", "bank_block_001", "seed_9256"),
    ("cold-9209-ws", "club_block_014", "seed_9282"),
]
#: (arm, the shell set it swaps in)
ARMS = (("flat", "flat"), ("flat2", "flat"), ("stoop", "stoop"))
NAV = re.compile(r"Baked navmesh on (\S+) \((\d+) polygons, (\d+) source vertices\)")
#: a stuck body this near a stoop's plan box (metres, the body's centre) is "at a stoop"
AT_STOOP = 1.0

sys.path.insert(0, str(F / "lot"))
sys.path.insert(0, str(F / "deli_counter"))
import walktest  # noqa: E402
import presets  # noqa: E402
import stoop as stoop_geom  # noqa: E402
from spec_loader import spec_from_dict  # noqa: E402


def _stoop_local():
    """Each rowhome's stoop in its own GLB's frame (Godot: x, height, z = Blender -y): its plan box
    ``(x0, x1, z0, z1)``, from `stoop.plan` -- Deli Counter's own numbers, the same in every arm."""
    out = {}
    for n in presets.EMPTY_ROWHOMES:
        p = stoop_geom.plan(spec_from_dict(presets.empty_rowhome(name=n, **presets.EMPTY_ROWHOMES[n])))
        out[n] = (p["x"] - p["width"] / 2.0, p["x"] + p["width"] / 2.0, -p["face_y"], -p["foot_y"])
    return out


STOOP_LOCAL = _stoop_local()


def _stoops(site_tscn):
    """Every placed rowhome's stoop in the level's frame: plan boxes ``(x0, x1, z0, z1)``, read off the
    copy's `site.tscn` (its ext_resources and each instance's Transform3D, rows then origin)."""
    t = site_tscn.read_text(encoding="utf-8")
    ext = {i: a for a, i in re.findall(r'\[ext_resource[^\]]*path="buildings/(gs_empty_rowhome_\w)\.glb"'
                                       r'[^\]]*id="([^"]+)"', t)}
    boxes = []
    for rid, tr in re.findall(r'\[node name="[^"]+" parent="[^"]*" instance=ExtResource\("([^"]+)"\)\]\s*\n'
                              r'transform = Transform3D\(([^)]*)\)', t):
        if rid not in ext:
            continue
        v = [float(x) for x in tr.split(",")]
        x0, x1, z0, z1 = STOOP_LOCAL[ext[rid]]
        pts = [(v[0] * x + v[2] * z + v[9], v[6] * x + v[8] * z + v[11]) for x in (x0, x1) for z in (z0, z1)]
        boxes.append((min(p[0] for p in pts), max(p[0] for p in pts), min(p[1] for p in pts),
                      max(p[1] for p in pts)))
    if not boxes:
        sys.exit("UNKNOWN SHAPE: no placed rowhome in %s" % site_tscn)
    return boxes


def _near(boxes, x, z):
    return min(((max(b[0] - x, 0.0, x - b[1]) ** 2 + max(b[2] - z, 0.0, z - b[3]) ** 2) ** 0.5) for b in boxes)


def _seed(job_log):
    first = job_log.read_text(encoding="utf-8", errors="replace").splitlines()[0]
    m = re.search(r"--seed (\d+)", first)
    if not m:
        sys.exit("UNKNOWN SHAPE: no --seed in %s" % job_log)
    return m.group(1)


def _pins(d):
    """Player-stuck events at a position recurring (to a millimetre) in two or more runs."""
    at = collections.defaultdict(set)
    count = collections.Counter()
    for e in d["events"]:
        if e["event"] != "PlayerStuck":
            continue
        k = tuple(round(v, 3) for v in e["position"])
        at[k].add(e["run_id"])
        count[k] += 1
    return (sum(count[k] for k, runs in at.items() if len(runs) >= 2),
            sum(1 for runs in at.values() if len(runs) >= 2))


def _walk_summary(report):
    """`rewalk.py`'s reading of a walk test's report. A director that could not start writes only its
    error, a verdict this keeps rather than refuses: ``{error, ok: false, regions, sim_seconds}``."""
    walkers = report.get("walkers")
    if report.get("ok") is False and isinstance(report.get("error"), str) and walkers is None:
        return {"ok": False, "error": report["error"], "walkers": {}, "walkers_not_ok": None, "targets": None,
                "stranded_anchors": None, "anchors_behind_a_barrier": None,
                "anchors_without_standing_room": None, "proof_failures": None,
                "sim_seconds": report.get("sim_seconds")}
    if not isinstance(walkers, list) or "ok" not in report:
        sys.exit("UNKNOWN SHAPE: a walk report without 'ok' and a walkers list")
    return {
        "ok": bool(report["ok"]),
        "walkers": {w["name"]: w["status"] for w in walkers},
        "walkers_not_ok": sum(1 for w in walkers if w["status"] != "ok" and not w["status"].startswith("ok(")),
        "targets": [sum(w["targets_reached"] for w in walkers), sum(w["targets_total"] for w in walkers)],
        "stranded_anchors": report.get("stranded_anchors"),
        "anchors_behind_a_barrier": report.get("anchors_behind_a_barrier"),
        "anchors_without_standing_room": report.get("anchors_without_standing_room"),
        "proof_failures": report.get("_proof_failures"),
        "sim_seconds": report.get("sim_seconds"),
    }


def _swap(copy, shells):
    """Every rowhome the copy's level carries, replaced by the shell set's: a fresh file (new time, new
    bytes), so the import pass sees it changed."""
    got = sorted((copy / "buildings").glob("gs_empty_rowhome_*.glb"))
    if not got:
        sys.exit("UNKNOWN SHAPE: no rowhome in %s" % (copy / "buildings"))
    for p in got:
        src = shells / p.name
        if not src.exists():
            sys.exit("no %s in %s: run build_flat.py first" % (p.name, shells))
        p.unlink()
        shutil.copyfile(src, p)
    return len(got)


def _laser_tag(lf, mission, seed, arm, shells, scr):
    name = "%s.laser_tag_evaluate.candidate.%s" % (mission, seed)
    n = _seed(lf / "jobs" / name / "1" / "job.log")
    dst = scr / ("%s_%s_%s" % (mission, seed, arm))
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(lf / "staging" / name, dst)
    swapped = _swap(dst, shells)
    shutil.rmtree(dst / "addons" / "laser_tag_tool")
    shutil.copytree(LT_ADDON, dst / "addons" / "laser_tag_tool")
    if "3d/physics_engine" in (dst / "project.godot").read_text(encoding="utf-8"):
        sys.exit("UNKNOWN SHAPE: %s names a physics engine" % (dst / "project.godot"))
    out = dst / "report.json"
    subprocess.run([GODOT, "--headless", "--path", str(dst), "--import"], cwd=str(dst), capture_output=True,
                   text=True, timeout=900, stdin=subprocess.DEVNULL)
    r = subprocess.run([GODOT, "--headless", "--fixed-fps", "60", "--path", str(dst), "-s",
                        "res://addons/laser_tag_tool/runners/run_map_eval.gd", "--", "--bake-nav",
                        "--map", "res://level.tscn", "--scenario", "res://mission_scenario.tres",
                        "--runs", "25", "--seed", n, "--output", str(out)],
                       cwd=str(dst), capture_output=True, text=True, timeout=1800, stdin=subprocess.DEVNULL)
    (scr / ("%s_%s_%s.log" % (mission, seed, arm))).write_text(r.stdout + r.stderr, encoding="utf-8")
    row = {"seed": n, "swapped": swapped, "exit": r.returncode,
           "nav": [list(m) for m in NAV.findall(r.stdout)]}
    if out.exists():
        d = json.loads(out.read_text(encoding="utf-8"))
        if "summary" not in d or "events" not in d:
            sys.exit("UNKNOWN SHAPE: a Laser Tag report without summary and events")
        pinned, places = _pins(d)
        boxes = _stoops(dst / "site.tscn")
        stuck = [{"event": e["event"], "run_id": e["run_id"], "source": e.get("source"), "time": e.get("time"),
                  "position": e["position"], "to_stoop": round(_near(boxes, e["position"][0], e["position"][2]), 3)}
                 for e in d["events"] if e["event"] in ("EnemyStuck", "PlayerStuck")]
        row.update(grade=d["grade"], score=d["overall_score"], pinned=pinned, pin_places=places,
                   summary=d["summary"], stuck=stuck, stoops=len(boxes),
                   stuck_at_stoop=sum(1 for s in stuck if s["to_stoop"] <= AT_STOOP))
        shutil.rmtree(dst)
    return row


def _walk(lf, mission, seed, arm, shells, scr, godot):
    name = "%s.walktest_navqa.candidate.%s" % (mission, seed)
    dst = scr / ("%s_%s_%s" % (mission, seed, arm))
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(lf / "staging" / name, dst)
    stale = dst / "site_navqa.walktest.json"
    if stale.exists():
        stale.unlink()      # the job's own report, which this run must not read back
    swapped = _swap(dst, shells)
    walktest.ensure_project(str(dst))
    # today's director, as `walktest.py`'s `main()` gives every run (`sync_addon`): nothing here patches
    # it, and a staged one older than Lot 0.117.0 never sees its map settle under today's fixed clock
    walktest.sync_addon(str(dst))
    log = io.StringIO()
    t0 = time.time()
    with contextlib.redirect_stdout(log):
        walktest.import_pass(godot, str(dst), timeout=900)
        walktest.run_one(godot, str(dst), str(dst / "site_navqa.tscn"), timeout=900)
    (scr / ("%s_%s_%s.log" % (mission, seed, arm))).write_text(log.getvalue(), encoding="utf-8")
    row = {"swapped": swapped, "seconds": round(time.time() - t0, 1),
           "nav": [l.strip() for l in log.getvalue().splitlines() if "polygon" in l.lower()][:4]}
    rep = dst / "site_navqa.walktest.json"
    if rep.exists():
        row["walk"] = _walk_summary(json.loads(rep.read_text(encoding="utf-8")))
        shutil.rmtree(dst)
    return row


def _fields(row, grader):
    """The fields compared between arms: everything read but the wall clock and the swap count."""
    if grader == "laser_tag":
        if "summary" not in row:
            return None
        out = {"grade": row["grade"], "score": row["score"], "pinned": row["pinned"],
               "pin_places": row["pin_places"], "nav": row["nav"], "stuck_at_stoop": row["stuck_at_stoop"]}
        out.update(("summary." + k, v) for k, v in row["summary"].items())
        return out
    if "walk" not in row:
        return None
    out = dict(("walk." + k, v) for k, v in row["walk"].items())
    out["nav"] = row["nav"]
    return out


def _diff(a, b):
    return sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--grader", required=True, choices=("laser_tag", "walk"))
    ap.add_argument("--only", nargs="*", default=None, help="labels (<mission>_<seed>) to grade")
    a = ap.parse_args()
    for arm in ("flat", "stoop"):
        if len(list((SHELLS / arm).glob("gs_empty_rowhome_*.glb"))) != 12:
            sys.exit("no twelve %s shells in %s: run build_flat.py first" % (arm, SHELLS / arm))
    godot = None
    if a.grader == "walk":
        godot, why = walktest.find_godot()
        if godot is None:
            sys.exit("no Godot: %s" % why)
    else:
        version = LT_ADDON.parent.parent / "VERSION"
        print("Laser Tag addon: %s (%s)" % (LT_ADDON, version.read_text().strip() if version.exists() else "?"))
    scr = F / "_scratch" / "stoop_breadth" / a.grader
    scr.mkdir(parents=True, exist_ok=True)
    out_path = HERE / ("results_%s.json" % a.grader)
    results = json.loads(out_path.read_text(encoding="utf-8")) if out_path.exists() else {}
    for ws, mission, seed in LOTS:
        label = "%s_%s" % (mission, seed)
        if a.only and label not in a.only:
            continue
        lf = F / "workspaces" / ws / ".level_factory"
        rows = {}
        for arm, shells in ARMS:
            if a.grader == "laser_tag":
                rows[arm] = _laser_tag(lf, mission, seed, arm, SHELLS / shells, scr)
            else:
                rows[arm] = _walk(lf, mission, seed, arm, SHELLS / shells, scr, godot)
        results[label] = {"workspace": ws, "arms": rows}
        out_path.write_text(json.dumps(results, indent=1, sort_keys=True), encoding="utf-8")
        f = {arm: _fields(rows[arm], a.grader) for arm, _s in ARMS}
        print("%s (%s, %d rowhomes swapped)" % (label, ws, rows["flat"]["swapped"]), flush=True)
        if any(v is None for v in f.values()):
            print("   NOT MEASURED: %s" % ", ".join(arm for arm, v in f.items() if v is None), flush=True)
            continue
        control = _diff(f["flat"], f["flat2"])
        if control:
            print("   CONTROL FAILED: flat and flat2 differ in %s" % ", ".join(control), flush=True)
        if a.grader == "laser_tag":
            for arm, _s in ARMS:
                r = rows[arm]
                s = r["summary"]
                near = min((x["to_stoop"] for x in r["stuck"]), default=None)
                print("   %-6s %-16s %5s  route %4s  player stuck %3s (pinned %3s at %2s places)  enemy stuck %3s"
                      "  deaths %3s  stuck at a stoop %d (nearest %s m)  nav %s"
                      % (arm, r["grade"], r["score"], s["route_completion_rate"], s["player_stuck_events"],
                         r["pinned"], r["pin_places"], s["enemy_stuck_events"], s["player_deaths"],
                         r["stuck_at_stoop"], near, r["nav"]), flush=True)
        else:
            for arm, _s in ARMS:
                w = rows[arm]["walk"]
                print("   %-6s %-4s  walkers not ok %2s  targets %s  stranded %s  behind a barrier %s"
                      "  no standing room %s  sim %s s%s" % (arm, "ok" if w["ok"] else "FAIL", w["walkers_not_ok"],
                                                            w["targets"], w["stranded_anchors"],
                                                            w["anchors_behind_a_barrier"],
                                                            w["anchors_without_standing_room"], w["sim_seconds"],
                                                            ("  ERROR " + w["error"]) if w.get("error") else ""),
                      flush=True)
        moved = _diff(f["flat"], f["stoop"])
        print("   stoop moved from flat: %s" % (", ".join(moved) if moved else "nothing read"), flush=True)
        for k in moved:
            print("      %-44s %s -> %s" % (k, f["flat"].get(k), f["stoop"].get(k)), flush=True)


if __name__ == "__main__":
    main()
