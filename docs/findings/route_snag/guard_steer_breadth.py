"""Laser Tag 0.31.0 over the factory's 16 lots: the guards walk as the crew does, keeping to the mesh and stepping
up (roadmap 242).

    python docs/findings/route_snag/guard_steer_breadth.py

`blocked_breadth.py`'s lots, its grading (`_grade`: a copy of each staged lot with the arm's addon, an import
pass, today's command, 25 runs from the job's seed, Godot Physics), three arms:

  0.30.0       Laser Tag's commit af09e20, exported -- the release before
  0.31.0       the repository's working tree, the change
  0.31.0 off   the working tree with the guards' new steering switched off in the copy: `keep_to_mesh` false
               and the harness giving a guard a step of 0

0.31.0 moves code the crew walks by into `LT_Steering` and adds two behaviours to the guards. THE CONTROL is
that `0.31.0 off` reads 0.30.0 exactly -- every summary field, the grade and the score -- on every lot: the
move changed nothing the crew does, and every difference in the 0.31.0 row is the guards' steering. A lot
where the control fails says so, and its 0.31.0 row means nothing.

0.31.0 moves the guards, so it moves fights: a lot a line, 0.30.0's grade, score, enemy stuck and blocked
against 0.31.0's, and under it every other summary field that moved, before -> after. Copies go to
`_scratch/guard_steer_breadth/` and are removed. Prints what it measured and stops;
`guard_steer_breadth.out.txt` is its output.
"""
import io
import pathlib
import shutil
import subprocess
import sys
import tarfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import blocked_breadth as bb  # noqa: E402  (its LOTS, _seed and _grade)

F = bb.F
SCR = F / "_scratch" / "guard_steer_breadth"
BEFORE = "af09e20"  # Laser Tag 0.30.0
ADDON = "addons/laser_tag_tool"
#: the two switches `0.31.0 off` turns in its copy, each asserted once
OFF = [
    ("scripts/enemy/LT_EnemyMovement.gd",
     "@export var keep_to_mesh: bool = true\n", "@export var keep_to_mesh: bool = false\n"),
    ("scripts/core/LT_MapEvalHarness.gd",
     "\t\tguard.max_step_up = scenario.player_max_step_up_m\n", "\t\tguard.max_step_up = 0.0\n"),
]
HEAD = ("grade", "overall_score")
COUNTS = ("enemy_stuck_events", "enemy_blocked_events")


def _export_before(dst):
    tar = subprocess.run(["git", "-C", str(F / "lasertag"), "archive", BEFORE], capture_output=True, check=True)
    # unpacked here, not by a `tar` on PATH: Windows' own reads a tape device unless told `-f -`
    with tarfile.open(fileobj=io.BytesIO(tar.stdout)) as t:
        t.extractall(dst, filter="data")
    return dst / ADDON


def _switched_off(dst):
    addon = dst / ADDON
    shutil.copytree(F / "lasertag" / ADDON, addon)
    shutil.copy(F / "lasertag" / "VERSION", dst / "VERSION")
    for rel, old, new in OFF:
        p = addon / rel
        raw = p.read_bytes()
        eol = b"\r\n" if b"\r\n" in raw else b"\n"
        text = raw.decode("utf-8").replace("\r\n", "\n")
        if text.count(old) != 1:
            sys.exit("UNKNOWN SHAPE: %d of %r in %s" % (text.count(old), old, rel))
        p.write_bytes(text.replace(old, new).encode("utf-8").replace(b"\n", eol))
    return addon


def _fmt(v):
    return ("%.3f" % v) if isinstance(v, float) else str(v)


def main():
    if SCR.exists():
        shutil.rmtree(SCR)
    SCR.mkdir(parents=True)
    addons = {"0.30.0": _export_before(SCR / "lasertag_0300"),
              "0.31.0": F / "lasertag" / ADDON,
              "0.31.0 off": _switched_off(SCR / "lasertag_0310_off")}
    for v, a in addons.items():
        ver = (a.parent.parent / "VERSION").read_text(encoding="utf-8").strip()
        print("%s: %s (%s)" % (v, a, ver), flush=True)
        if not ver.endswith(v.split()[0]):
            sys.exit("UNKNOWN SHAPE: %s's VERSION reads %r" % (a, ver))
    totals = {"stuck_0300": 0, "stuck_0310": 0, "blocked_0300": 0, "blocked_0310": 0}
    failed = 0
    for ws, mission, seed_name in bb.LOTS:
        lf = F / "workspaces" / ws / ".level_factory"
        name = "%s.laser_tag_evaluate.candidate.%s" % (mission, seed_name)
        seed = bb._seed(lf / "jobs" / name / "1" / "job.log")
        rows = {v: bb._grade(lf / "staging" / name, a,
                             SCR / ("%s_%s_%s" % (mission, seed_name, v.replace(" ", "_").replace(".", ""))), seed)
                for v, a in addons.items()}
        if any(r is None for r in rows.values()):
            print("%s %s: NOT MEASURED (%s)" % (mission, seed_name,
                                                 ", ".join(v for v, r in rows.items() if r is None)), flush=True)
            continue
        a, b, off = rows["0.30.0"], rows["0.31.0"], rows["0.31.0 off"]
        control = sorted(k for k in set(a["summary"]) | set(off["summary"])
                         if a["summary"].get(k) != off["summary"].get(k))
        control += [k for k in HEAD if a[k] != off[k]]
        sa, sb = a["summary"], b["summary"]
        totals["stuck_0300"] += sa["enemy_stuck_events"]
        totals["stuck_0310"] += sb["enemy_stuck_events"]
        totals["blocked_0300"] += sa.get("enemy_blocked_events", 0)
        totals["blocked_0310"] += sb.get("enemy_blocked_events", 0)
        print("%-20s %-9s %-16s %3s -> %-16s %3s  enemy stuck %3d -> %3d, blocked %3d -> %3d%s" % (
            mission, seed_name, a["grade"], a["overall_score"], b["grade"], b["overall_score"],
            sa["enemy_stuck_events"], sb["enemy_stuck_events"], sa.get("enemy_blocked_events", 0),
            sb.get("enemy_blocked_events", 0),
            "" if not control else "   CONTROL FAILED: 0.31.0 off differs from 0.30.0 in %s" % ", ".join(control)),
            flush=True)
        if control:
            failed += 1
            continue
        moved = sorted(k for k in set(sa) | set(sb) if k not in COUNTS and sa.get(k) != sb.get(k))
        if moved:
            print("    also moved: %s" % "; ".join("%s %s -> %s" % (k, _fmt(sa.get(k)), _fmt(sb.get(k)))
                                               for k in moved), flush=True)
    shutil.rmtree(SCR, ignore_errors=True)
    print("over the lots measured: enemy stuck %d under 0.30.0, %d under 0.31.0; blocked %d -> %d; "
          "the control failed on %d" % (totals["stuck_0300"], totals["stuck_0310"], totals["blocked_0300"],
                                         totals["blocked_0310"], failed))


if __name__ == "__main__":
    main()
