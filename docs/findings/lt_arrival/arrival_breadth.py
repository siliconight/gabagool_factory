"""Laser Tag 0.32.0 over the factory's sixteen lots and the stranded objective: what an arrival at the point moves
(roadmap 246).

    python docs/findings/lt_arrival/arrival_breadth.py

`docs/findings/route_snag/blocked_breadth.py`'s lots and grading (`_grade`: a copy of each staged evaluation with
the arm's addon, an import pass, Laser Tag's own command, 25 runs from the job's seed, Godot Physics), and one lot
more: cold run 9185's restaurant_row_001 seed_9003, whose objective stands on a navmesh island
(`arrival_trace.py`). Two arms:

  0.31.0    Laser Tag's HEAD, exported -- the release before
  0.32.0    the repository's working tree, the change

0.32.0 changes what `_advance_route` counts when a bot's path stops short of its route point; where every point is
reachable the two take the same branch. THE CONTROL, then, is every lot whose route points are all reachable:
there 0.32.0 must read 0.31.0 exactly -- every summary field, the grade and the score -- and a lot that moves says
so with every field that moved, before -> after. Copies go to `_scratch/arrival_breadth/` and are removed. Prints
what it measured and stops; `arrival_breadth.out.txt` is its output.
"""
import io
import pathlib
import shutil
import subprocess
import sys
import tarfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "route_snag"))
import blocked_breadth as bb  # noqa: E402  (its LOTS, _seed and _grade)

F = bb.F
SCR = F / "_scratch" / "arrival_breadth"
ADDON = "addons/laser_tag_tool"
LOTS = bb.LOTS + [("cold-9185-ws", "restaurant_row_001", "seed_9003")]
HEAD = ("grade", "overall_score")


def _export_head(dst):
    tar = subprocess.run(["git", "-C", str(F / "lasertag"), "archive", "HEAD"], capture_output=True, check=True)
    # unpacked here, not by a `tar` on PATH: Windows' own reads a tape device unless told `-f -`
    with tarfile.open(fileobj=io.BytesIO(tar.stdout)) as t:
        t.extractall(dst, filter="data")
    return dst / ADDON


def _fmt(v):
    return ("%.3f" % v) if isinstance(v, float) else str(v)


def main():
    if SCR.exists():
        shutil.rmtree(SCR)
    SCR.mkdir(parents=True)
    addons = {"0.31.0": _export_head(SCR / "lasertag_0310"), "0.32.0": F / "lasertag" / ADDON}
    for v, a in addons.items():
        ver = (a.parent.parent / "VERSION").read_text(encoding="utf-8").strip()
        print("%s: %s (%s)" % (v, a, ver), flush=True)
        if not ver.endswith(v):
            sys.exit("UNKNOWN SHAPE: %s's VERSION reads %r" % (a, ver))
    same = moved_lots = 0
    for ws, mission, seed_name in LOTS:
        lf = F / "workspaces" / ws / ".level_factory"
        name = "%s.laser_tag_evaluate.candidate.%s" % (mission, seed_name)
        seed = bb._seed(lf / "jobs" / name / "1" / "job.log")
        rows = {v: bb._grade(lf / "staging" / name, a, SCR / ("%s_%s_%s" % (mission, seed_name, v.replace(".", ""))),
                             seed)
                for v, a in addons.items()}
        if any(r is None for r in rows.values()):
            print("%s %s %s: NOT MEASURED (%s)" % (ws, mission, seed_name,
                                                    ", ".join(v for v, r in rows.items() if r is None)), flush=True)
            continue
        a, b = rows["0.31.0"], rows["0.32.0"]
        sa, sb = a["summary"], b["summary"]
        moved = sorted(k for k in set(sa) | set(sb) if sa.get(k) != sb.get(k))
        moved_head = [k for k in HEAD if a.get(k) != b.get(k)]
        line = "%-30s %-20s %-9s %-16s %3s -> %-16s %3s  completion %s -> %s, progress %s -> %s" % (
            ws, mission, seed_name, a["grade"], a["overall_score"], b["grade"], b["overall_score"],
            _fmt(sa.get("route_completion_rate")), _fmt(sb.get("route_completion_rate")),
            _fmt(sa.get("route_progress_rate")), _fmt(sb.get("route_progress_rate")))
        if not moved and not moved_head:
            same += 1
            print(line + "   SAME", flush=True)
        else:
            moved_lots += 1
            print(line + "   MOVED", flush=True)
            print("    moved: %s" % "; ".join("%s %s -> %s" % (k, _fmt(sa.get(k)), _fmt(sb.get(k))) for k in moved),
                  flush=True)
    shutil.rmtree(SCR, ignore_errors=True)
    print("of %d lots measured: %d read 0.31.0 exactly, %d moved" % (same + moved_lots, same, moved_lots))


if __name__ == "__main__":
    main()
