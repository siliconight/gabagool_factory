"""Re-walk the kept workspaces' staged walk tests with the crew's body (roadmap 208, measure first).

    python rewalk.py --variant as_run|crew_body|radius_only|floor_only [--only LABEL ...]

WHAT IT RE-WALKS. Every `*.walktest_navqa.candidate.*` staging folder under
the kept cold-run workspaces (cold-9193-ws .. cold-9204-ws), de-duplicated by
content -- the navqa scene, the site scene, the director script and the
building files' names and sizes -- because cold runs 9196 to 9203 repeat
missions and seeds byte for byte. Each distinct one is labelled by its first
occurrence, `<run>_<mission>_<seed>`.

HOW. Each walk is a COPY of the staging folder under `_scratch/`, with its
own `addons/heist_nav_qa/nav_qa_director.gd` patched for the variant, run
through `lot/walktest.py`'s own steps -- `ensure_project`, `check_buildings`,
`import_pass`, `run_one` -- and NOT its `main()`. `main()` calls
`sync_addon`, which copies the checkout's addon over the project's before
every run, so a patched copy walked through it would walk the shipped body
and report a null result from a dial that was never turned.

THE VARIANTS. The director builds its walker at `AGENT_RADIUS * 0.7` (0.28 m
from the 0.40 bake radius) on a 56 degree floor (`DC_NAV_SLOPE` + 1).
Laser Tag's crew pill is the contract's `characters.player.radius_m` (0.35)
and sets no floor angle, so it stands on CharacterBody3D's default, 45.
- `as_run`: the copy unpatched. The control: it must give the job's own
  verdict, or nothing else here means anything.
- `crew_body`: radius 0.35 and floor 45, the director's step-up kept.
- `crew_full`: `crew_body` with Laser Tag's step-up in place of the
  director's (THE STEP, below the variant table).
- `radius_only`, `floor_only`: one of the two, to attribute a failure.
THE WAYPOINT RADIUS STAYS THE DIRECTOR'S, 0.072 m (`AGENT_RADIUS * 0.18`).
*RETRACTED, kept above what replaced it:* the first version set `DC_QA_WP`
to the director's derivation applied to the crew's body -- 60% of (bake
radius - walker radius), 0.6 * (0.40 - 0.35) = 0.03 m -- "so a failure is
not the walker cutting a corner tuned for a thinner body". It froze every
walker at its first waypoint: restaurant_row seed_9003, 16 of 16 stuck
within 18 simulated seconds, each one standing over its waypoint with the
whole 0.6 m gap vertical (`results_crew_body_wp003_refuted.json`, three
walks). A body moves 4 m/s / 60 Hz = 0.067 m a physics frame, so a capture
radius under that can be stepped over forever. The director's rule needs the
radius above the frame step AND inside the corner margin, and for a 0.35
body on the contract's 0.40 bake (cell 0.10, no ceiling) the margin is
0.05 -- under the step, so no radius does both. The default is kept: corners
are consumed by `_passed` (past the waypoint along the next leg), and the
proximity radius is the secondary rule. A corner the wider body clips by up
to 0.022 m is a contact it slides along, and a walker it stops says so in
the log ("touching: ..."), which is where a failure gets attributed.

Writes, beside this file: `reports/<variant>/<label>.walktest.json` (the
director's report, verbatim) and `results_<variant>.json` (one row a label:
the verdict, each walker's status, the counts the report carries, the
recorded verdict, the wall-clock seconds). Prints what it measured and
stops. The scratch copies are deleted once their report is kept.
"""
import argparse
import contextlib
import hashlib
import io
import json
import os
import pathlib
import shutil
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
SCRATCH = ROOT / "_scratch" / "2026-10-08_walktest_body"
RUNS = range(9193, 9205)
DIRECTOR = pathlib.Path("addons") / "heist_nav_qa" / "nav_qa_director.gd"
RADIUS_LINE = "capsule.radius = AGENT_RADIUS * 0.7"
FLOOR_LINE = 'body.floor_max_angle = deg_to_rad(_envf("DC_NAV_SLOPE", 55.0) + 1.0)'

sys.path.insert(0, str(ROOT / "lot"))
sys.path.insert(0, str(ROOT / "deli_counter"))
import agent_contract   # noqa: E402
import walktest         # noqa: E402

CREW_RADIUS = agent_contract.body_radius()
CREW_FLOOR_DEG = 45.0       # CharacterBody3D.floor_max_angle's default; Laser Tag sets none
#: (crew radius, crew floor, crew step)
VARIANTS = {
    "as_run": (False, False, False),
    "crew_body": (True, True, False),
    "radius_only": (True, False, False),
    "floor_only": (False, True, False),
    "crew_full": (True, True, True),
}

# THE STEP. The director's step-up lifts 0.5, 0.35 or 0.2 m on any wall
# contact and moves on if the lift and a 0.35 m move clear -- it never asks
# what it lands on, so at a 45 degree floor a steeper ramp reads as a wall and
# the walker climbs it by repeated lifts. `crew_full` replaces that block
# with Laser Tag 0.24.0's `_try_step_up` (LT_BotPlayerController.gd): a TOP
# found straight down a body-width ahead, its normal inside the body's
# floor_max_angle and its rise inside the step, the top's height lifted
# first and the full lift second. Laser Tag's origin is the body's feet; the
# director's is the capsule's centre, so the copy takes the feet as half the
# capsule's height below it. Anchored on the block as every kept staging
# copy carries it (36 of 36, line endings normalised).
STEP_OLD = "\n".join([
    "\t\tvar fwd := Vector3(vel.x, 0.0, vel.z).normalized()",
    "\t\tvar stepped := false",
    "\t\tvar lifts_blocked := 0",
    "\t\tvar lifts := [STEP_UP, STEP_UP * 0.7, STEP_UP * 0.4]",
    "\t\tfor lift in lifts:",
    "\t\t\tvar up := Vector3(0.0, float(lift), 0.0)",
    "\t\t\tif body.test_move(body.global_transform, up):",
    "\t\t\t\tlifts_blocked += 1",
    "\t\t\t\tcontinue",
    "\t\t\tvar lifted := body.global_transform.translated(up)",
    "\t\t\tif body.test_move(lifted, fwd * STEP_FWD):",
    "\t\t\t\tcontinue",
    "\t\t\tbody.global_position += up + fwd * STEP_FWD",
    "\t\t\tbody.velocity.y = 0.0",
    "\t\t\tstepped = true",
    "\t\t\tbreak",
    "\t\tif stepped:",
    "\t\t\tw.erase(\"step_fail\")",
    "\t\telse:",
    "\t\t\tw[\"step_fail\"] = (\"nothing overhead to lift into (%d/%d probes blocked)\"",
    "\t\t\t\t\t\t\t  % [lifts_blocked, lifts.size()]) \\",
    "\t\t\t\tif lifts_blocked == lifts.size() \\",
    "\t\t\t\telse \"lifted clear but nothing to step onto ahead\"",
]) + "\n"
STEP_NEW = "\n".join([
    "\t\tvar fwd := Vector3(vel.x, 0.0, vel.z).normalized()",
    "\t\tvar stepped := false",
    "\t\tvar lifts_blocked := 0",
    "\t\t# CREW STEP -- a measurement copy (docs/findings/walktest_crew_body/,",
    "\t\t# roadmap 208), not the shipped director: Laser Tag 0.24.0's rule.",
    "\t\tvar crew_shape: CollisionShape3D = body.get_child(0) as CollisionShape3D",
    "\t\tvar crew_r: float = 0.35",
    "\t\tif crew_shape != null and crew_shape.shape is CapsuleShape3D:",
    "\t\t\tcrew_r = (crew_shape.shape as CapsuleShape3D).radius",
    "\t\tvar crew_reach: float = crew_r + 0.05",
    "\t\tvar crew_feet: Vector3 = body.global_position - Vector3(0.0, AGENT_HEIGHT * 0.5, 0.0)",
    "\t\tvar crew_probe: Vector3 = crew_feet + fwd * crew_reach",
    "\t\tvar crew_excl: Array[RID] = [body.get_rid()]",
    "\t\tvar crew_q: PhysicsRayQueryParameters3D = PhysicsRayQueryParameters3D.create(",
    "\t\t\tcrew_probe + Vector3.UP * (STEP_UP + 0.05),",
    "\t\t\tcrew_probe + Vector3.DOWN * 0.05, 1, crew_excl)",
    "\t\tvar crew_hit: Dictionary = body.get_world_3d().direct_space_state.intersect_ray(crew_q)",
    "\t\tvar crew_why: String = \"\"",
    "\t\tvar lifts: Array = []",
    "\t\tif body.get_wall_normal().dot(fwd) > -0.3:",
    "\t\t\tcrew_why = \"the wall is not ahead\"",
    "\t\telif crew_hit.is_empty():",
    "\t\t\tcrew_why = \"no top ahead\"",
    "\t\telse:",
    "\t\t\tvar crew_top: Vector3 = crew_hit[\"position\"]",
    "\t\t\tvar crew_n: Vector3 = crew_hit[\"normal\"]",
    "\t\t\tvar crew_rise: float = crew_top.y - crew_feet.y",
    "\t\t\tvar crew_deg: float = rad_to_deg(crew_n.angle_to(Vector3.UP))",
    "\t\t\tif crew_rise <= 0.01 or crew_rise > STEP_UP:",
    "\t\t\t\tcrew_why = \"the top rises %.2f m\" % crew_rise",
    "\t\t\telif crew_n.angle_to(Vector3.UP) > body.floor_max_angle:",
    "\t\t\t\tcrew_why = \"the top is %.1f deg, steeper than the floor\" % crew_deg",
    "\t\t\telse:",
    "\t\t\t\tlifts = [crew_rise + 0.05, STEP_UP + 0.05]",
    "\t\tfor lift in lifts:",
    "\t\t\tvar up := Vector3(0.0, float(lift), 0.0)",
    "\t\t\tif body.test_move(body.global_transform, up):",
    "\t\t\t\tlifts_blocked += 1",
    "\t\t\t\tcontinue",
    "\t\t\tvar lifted := body.global_transform.translated(up)",
    "\t\t\tif body.test_move(lifted, fwd * crew_reach):",
    "\t\t\t\tcontinue",
    "\t\t\tbody.global_position += up + fwd * crew_reach",
    "\t\t\tbody.velocity.y = 0.0",
    "\t\t\tstepped = true",
    "\t\t\tbreak",
    "\t\tif stepped:",
    "\t\t\tw.erase(\"step_fail\")",
    "\t\telif crew_why != \"\":",
    "\t\t\tw[\"step_fail\"] = \"crew step refused: \" + crew_why",
    "\t\telse:",
    "\t\t\tw[\"step_fail\"] = (\"nothing overhead to lift into (%d/%d probes blocked)\"",
    "\t\t\t\t\t\t\t  % [lifts_blocked, lifts.size()]) \\",
    "\t\t\t\tif lifts_blocked == lifts.size() \\",
    "\t\t\t\telse \"lifted clear but nothing to step onto ahead\"",
]) + "\n"


def distinct_walks():
    seen, out = {}, []
    for n in RUNS:
        staging = ROOT / "workspaces" / f"cold-{n}-ws" / ".level_factory" / "staging"
        for d in sorted(staging.glob("*.walktest_navqa.candidate.*")):
            h = hashlib.sha256()
            for rel in ("site_navqa.tscn", "site.tscn", str(DIRECTOR)):
                p = d / rel
                h.update(p.read_bytes() if p.exists() else b"MISSING")
            for g in sorted((d / "buildings").glob("*")):
                h.update(g.name.encode())
                h.update(str(g.stat().st_size).encode())
            dig = h.hexdigest()[:12]
            if dig in seen:
                continue
            mission = d.name.split(".walktest")[0]
            seed = d.name.split(".candidate.")[1]
            seen[dig] = True
            out.append({"label": f"{n}_{mission}_{seed}", "src": d, "digest": dig})
    return out


def patch(copy, radius, floor, step):
    path = copy / DIRECTOR
    data = path.read_bytes()
    crlf = data.count(b"\r\n")
    if crlf not in (0, data.count(b"\n")):
        raise SystemExit(f"{path}: mixed line endings")
    text = data.decode("utf-8").replace("\r\n", "\n")
    for old, on, new in ((RADIUS_LINE, radius, f"capsule.radius = {CREW_RADIUS!r}"),
                         (FLOOR_LINE, floor, f"body.floor_max_angle = deg_to_rad({CREW_FLOOR_DEG!r})"),
                         (STEP_OLD, step, STEP_NEW)):
        if not on:
            continue
        if text.count(old) != 1:
            raise SystemExit(f"{path}: {old.splitlines()[0]!r}... found {text.count(old)} times")
        text = text.replace(old, new)
    if crlf:
        text = text.replace("\n", "\r\n")     # as shipped
    path.write_bytes(text.encode("utf-8"))


def summary(report):
    walkers = report.get("walkers")
    if not isinstance(walkers, list) or "ok" not in report:
        raise SystemExit("a report without 'ok' and a walkers list: not the shape this reads")
    return {
        "ok": bool(report["ok"]),
        "walkers": {w["name"]: w["status"] for w in walkers},
        # `ok(N vertical leg(s) via ladder)` is the director's ok for a walker
        # that climbed a ladder
        "walkers_not_ok": sum(1 for w in walkers
                              if w["status"] != "ok" and not w["status"].startswith("ok(")),
        "targets": [sum(w["targets_reached"] for w in walkers), sum(w["targets_total"] for w in walkers)],
        "stranded_anchors": report.get("stranded_anchors"),
        "anchors_behind_a_barrier": report.get("anchors_behind_a_barrier"),
        "anchors_without_standing_room": report.get("anchors_without_standing_room"),
        "proof_failures": report.get("_proof_failures"),
        "sim_seconds": report.get("sim_seconds"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", required=True, choices=sorted(VARIANTS))
    ap.add_argument("--only", nargs="*", default=None, help="labels to walk; default every distinct one")
    ap.add_argument("--timeout", type=int, default=600)
    a = ap.parse_args()
    radius, floor, step = VARIANTS[a.variant]
    godot, reason = walktest.find_godot()
    if godot is None:
        raise SystemExit(f"no Godot: {reason}")
    if "DC_QA_WP" in os.environ:
        raise SystemExit("DC_QA_WP is set in this shell; the director's own waypoint radius is the one measured")
    print(f"variant {a.variant}: radius {CREW_RADIUS if radius else 'as run'}, "
          f"floor {CREW_FLOOR_DEG if floor else 'as run'}, waypoint radius the director's")
    walks = distinct_walks()
    if a.only:
        walks = [w for w in walks if w["label"] in a.only]
        missing = set(a.only) - {w["label"] for w in walks}
        if missing:
            raise SystemExit(f"unknown labels: {sorted(missing)}")
    out_path = HERE / f"results_{a.variant}.json"
    results = json.loads(out_path.read_text(encoding="utf-8")) if out_path.exists() else {}
    for w in walks:
        copy = SCRATCH / a.variant / w["label"]
        if copy.exists():
            shutil.rmtree(copy)
        shutil.copytree(w["src"], copy)
        stale = copy / "site_navqa.walktest.json"
        if stale.exists():
            stale.unlink()      # the job's own report, which this run must not read back
        patch(copy, radius, floor, step)
        walktest.ensure_project(str(copy))
        if walktest.check_buildings(str(copy)):
            raise SystemExit(f"{copy}: missing buildings")
        t0 = time.time()
        log = io.StringIO()
        with contextlib.redirect_stdout(log):
            walktest.import_pass(godot, str(copy))
            walktest.run_one(godot, str(copy), str(copy / "site_navqa.tscn"), timeout=a.timeout)
        secs = round(time.time() - t0, 1)
        (SCRATCH / a.variant / f"{w['label']}.log").write_text(log.getvalue(), encoding="utf-8")
        rep_path = copy / "site_navqa.walktest.json"
        recorded = json.loads((w["src"] / "site_navqa.walktest.json").read_text(encoding="utf-8"))
        row = {"digest": w["digest"], "src": str(w["src"].relative_to(ROOT)), "seconds": secs,
               "recorded": summary(recorded)}
        if rep_path.exists():
            report = json.loads(rep_path.read_text(encoding="utf-8"))
            keep = HERE / "reports" / a.variant / f"{w['label']}.walktest.json"
            keep.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(rep_path, keep)
            row["walked"] = summary(report)
        else:
            row["walked"] = None    # no report: a timeout or a crash; the log says which
        results[w["label"]] = row
        out_path.write_text(json.dumps(results, indent=1, sort_keys=True), encoding="utf-8")
        if row["walked"] is not None:
            shutil.rmtree(copy)
        got = "NO REPORT" if row["walked"] is None else (
            "ok" if row["walked"]["ok"] else "FAIL (%d walker(s) not ok)" % row["walked"]["walkers_not_ok"])
        print(f"{w['label']:40s} {got:28s} recorded {'ok' if row['recorded']['ok'] else 'FAIL'}  {secs:6.1f} s",
              flush=True)


if __name__ == "__main__":
    main()
