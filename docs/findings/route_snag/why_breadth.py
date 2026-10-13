"""How many of Laser Tag's player-stuck events are bots standing to fight, over `engine_breadth.py`'s 16
lots under both engines (roadmap 242, 2026-10-12).

    python docs/findings/route_snag/why_breadth.py --expect docs/findings/route_snag/engine_breadth.out.txt
    LT_ADDON=<draft addon> python docs/findings/route_snag/why_breadth.py --expect .../engine_breadth_028.out.txt

`_update_stuck` closes a 4 s window and records PlayerStuck when the body moved less than 0.5 m and
no enemy is in sight AT THAT INSTANT -- and costs the traversal score 10 points for any at all. A bot
that stood to fight all window (`advance_while_engaging` off, the factory's setting: it stops) and
lost sight of its enemy as the window closed is counted. `pin_trace.py census --why` found 18 of the
21 stuck events Laser Tag 0.28.0's draft added on five lots were such windows. This asks the same of
every lot, each run as `engine_breadth.py` ran it (the same copy, addon, engine and command), its bot
controller instrumented the way `pin_trace.py --why` does it (prints only).

THE CONTROL: each lot's row -- grade, score, route, player stuck, pinned, places, enemy stuck, deaths --
must equal the row `--expect`'s file printed for the same lot and engine, or the prints moved the run
and the lot is not counted. A stuck event is a FIGHT if its bot had an enemy in sight in at least half
the window's frames. It prints what it measured and stops.
"""
import collections
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import engine_breadth as EB   # noqa: E402
import pin_trace as PT        # noqa: E402

LINE = re.compile(r"^\[LT stuck\] (\S+) \(([-\d.]+), ([-\d.]+), ([-\d.]+)\) moved ([\d.]+) m, "
                  r"an enemy in sight (\d+) of (\d+) frames$")


def _expected(path):
    rows, lot = {}, None
    for line in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        m = re.match(r"^(\S+) (seed_\d+) \(seed", line)
        if m:
            lot = (m.group(1), m.group(2))
            continue
        m = re.match(r"^   (godot|godot2|jolt)\s+(.*)$", line)
        if m and lot:
            rows[(lot[0], lot[1], m.group(1))] = m.group(2).rstrip()
    if not rows:
        sys.exit("UNKNOWN SHAPE: no rows in %s" % path)
    return rows


def main():
    if "--expect" not in sys.argv:
        sys.exit(__doc__)
    expect = _expected(sys.argv[sys.argv.index("--expect") + 1])
    addon = pathlib.Path(os.environ.get("LT_ADDON") or EB.LT_ADDON)
    version = addon.parent.parent / "VERSION"
    print("Laser Tag addon: %s (%s)" % (addon, version.read_text().strip() if version.exists() else "?"), flush=True)
    scr = EB.F / "_scratch" / "why_breadth"
    if scr.exists():
        shutil.rmtree(scr)
    scr.mkdir(parents=True)
    totals = collections.defaultdict(lambda: [0, 0, 0])   # engine -> [stuck, fights, lots counted]
    for ws, mission, seed in EB.LOTS:
        lf = EB.F / "workspaces" / ws / ".level_factory"
        name = "%s.laser_tag_evaluate.candidate.%s" % (mission, seed)
        n = EB._seed(lf / "jobs" / name / "1" / "job.log")
        for arm in ("godot", "jolt"):
            dst = scr / ("%s_%s_%s" % (mission, seed, arm))
            shutil.copytree(lf / "staging" / name, dst)
            shutil.rmtree(dst / "addons" / "laser_tag_tool")
            shutil.copytree(addon, dst / "addons" / "laser_tag_tool")
            if arm == "jolt":
                pg = dst / "project.godot"
                text = pg.read_text(encoding="utf-8")
                if "3d/physics_engine" in text:
                    sys.exit("UNKNOWN SHAPE: %s already names a physics engine" % pg)
                pg.write_text(text.rstrip("\n") + '\n\n[physics]\n\n3d/physics_engine="Jolt Physics"\n',
                              encoding="utf-8", newline="\n")
            PT._why(dst)
            out = dst / "report.json"
            proc = PT._run(dst, 25, n, out)
            report = json.loads(out.read_text(encoding="utf-8")) if out.exists() else None
            shutil.rmtree(dst)
            label = "%s %s %s" % (mission, seed, arm)
            if report is None:
                print("%-40s NOT MEASURED (exit %d)" % (label, proc.returncode), flush=True)
                continue
            row = EB._fmt(EB._row(report)).rstrip()
            want = expect.get((mission, seed, arm))
            if row != want:
                print("%-40s CONTROL FAILED: %s   (expected %s)" % (label, row, want), flush=True)
                continue
            said = [ln for ln in proc.stdout.splitlines() if ln.startswith("[LT stuck] ")]
            events = [e for e in report["events"] if e["event"] == "PlayerStuck"]
            if len(said) != len(events):
                print("%-40s UNKNOWN SHAPE: %d stuck lines for %d events" % (label, len(said), len(events)))
                continue
            fights = 0
            for e, ln in zip(events, said):
                m = LINE.match(ln)
                if m is None or m.group(1) != e["source"]:
                    sys.exit("UNKNOWN SHAPE: %r against %r" % (ln, e))
                fights += int(m.group(6)) * 2 >= int(m.group(7))
            totals[arm][0] += len(events)
            totals[arm][1] += fights
            totals[arm][2] += 1
            print("%-40s %s   stuck %3d, fights %3d" % (label, row[:28], len(events), fights), flush=True)
    shutil.rmtree(scr, ignore_errors=True)
    for arm in ("godot", "jolt"):
        s, f, lots = totals[arm]
        print("%s: %d lots whose control held, %d player-stuck events, %d of them fights (%d left)" % (
            "Godot Physics" if arm == "godot" else "Jolt", lots, s, f, s - f))
    return 0


if __name__ == "__main__":
    sys.exit(main())
